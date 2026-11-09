<?php
// H1 - Medicion del proceso ACTUAL del simulador (SimulacroController@show y @evaluar).
// Ejecuta las mismas consultas SQL que genera Eloquent, sobre una COPIA temporal de los datos
// reales (base h1_medicion_tmp, que se borra al terminar). La base plataforma_med no se modifica.
//
// Protocolo: calentar -> repetir -> promediar -> escalar -> mismas condiciones.
// Uso: C:\xampp\php\php.exe h1\medir.php
declare(strict_types=1);

const ORIGEN = 'plataforma_med';
const BD = 'h1_medicion_tmp';
const CALENTAMIENTOS = 2;
const REPETICIONES = 10;
const REPETICIONES_CONCURRENCIA = 3;
const TODAS = [1, 2, 3, 4, 5];

function conectar(?string $bd = BD): PDO
{
    $dsn = 'mysql:host=127.0.0.1;port=3306;charset=utf8mb4' . ($bd ? ";dbname=$bd" : '');
    // Mismas opciones que usa Laravel por defecto
    return new PDO($dsn, 'root', '', [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);
}

function prepararCopia(): int
{
    $pdo = conectar(null);
    $pdo->exec('DROP DATABASE IF EXISTS ' . BD);
    $pdo->exec('CREATE DATABASE ' . BD . ' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
    foreach (['materias', 'preguntas', 'simulacros'] as $tabla) {
        $pdo->exec('CREATE TABLE ' . BD . ".$tabla LIKE " . ORIGEN . ".$tabla");
        $pdo->exec('INSERT INTO ' . BD . ".$tabla SELECT * FROM " . ORIGEN . ".$tabla");
    }
    // Tabla de la migracion 2026_07_28_220620_create_simulacro_respuestas_table
    $pdo->exec('CREATE TABLE ' . BD . '.simulacro_respuestas (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        simulacro_id BIGINT UNSIGNED NOT NULL,
        pregunta_id BIGINT UNSIGNED NOT NULL,
        materia_id BIGINT UNSIGNED NOT NULL,
        respuesta_usuario VARCHAR(1) NULL,
        es_correcta TINYINT(1) NOT NULL DEFAULT 0,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL,
        FOREIGN KEY (simulacro_id) REFERENCES simulacros(id) ON DELETE CASCADE,
        FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
        FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
    )');
    return (int) conectar()->query('SELECT MIN(id) FROM simulacros')->fetchColumn();
}

// --- SimulacroController@show: Pregunta::whereIn(...)->inRandomOrder()->limit(k)->get()
function generarExamen(PDO $pdo, array $materias, int $k): array
{
    $marcadores = implode(', ', array_fill(0, count($materias), '?'));
    $st = $pdo->prepare("select * from `preguntas` where `materia_id` in ($marcadores) order by RAND() limit $k");
    $st->execute($materias);
    return $st->fetchAll(PDO::FETCH_ASSOC);
}

// --- SimulacroController@evaluar: findOrFail + (find + create) por respuesta + save
function corregirExamen(PDO $pdo, int $simulacroId, array $respuestas): int
{
    $st = $pdo->prepare('select * from `simulacros` where `simulacros`.`id` = ? limit 1');
    $st->execute([$simulacroId]);
    $st->fetch();

    $correctas = 0;
    foreach ($respuestas as $preguntaId => $respuesta) {
        $st = $pdo->prepare('select * from `preguntas` where `preguntas`.`id` = ? limit 1');
        $st->execute([$preguntaId]);
        $pregunta = $st->fetch(PDO::FETCH_ASSOC);
        if (!$pregunta) {
            continue;
        }
        $respuestaUsuario = $respuesta !== '' ? strtoupper($respuesta) : null;
        $esCorrecta = $respuestaUsuario === $pregunta['respuesta'];
        if ($esCorrecta) {
            $correctas++;
        }
        $ahora = date('Y-m-d H:i:s');
        $pdo->prepare('insert into `simulacro_respuestas` (`simulacro_id`, `pregunta_id`, `materia_id`, '
            . '`respuesta_usuario`, `es_correcta`, `updated_at`, `created_at`) values (?, ?, ?, ?, ?, ?, ?)')
            ->execute([$simulacroId, $pregunta['id'], $pregunta['materia_id'], $respuestaUsuario,
                (int) $esCorrecta, $ahora, $ahora]);
    }
    $pdo->prepare('update `simulacros` set `cant_respuestas_correctas` = ?, `updated_at` = ? where `id` = ?')
        ->execute([$correctas, date('Y-m-d H:i:s'), $simulacroId]);
    return $correctas;
}

function responder(array $examen): array
{
    // El estudiante marca A-E al azar y deja ~10 % en blanco (como hace la vista al acabarse el tiempo)
    $respuestas = [];
    foreach ($examen as $p) {
        $respuestas[$p['id']] = mt_rand(1, 10) === 1 ? '' : ['A', 'B', 'C', 'D', 'E'][mt_rand(0, 4)];
    }
    return $respuestas;
}

function ms(int $desde): float
{
    return (hrtime(true) - $desde) / 1e6;
}

function estadisticas(array $t): array
{
    $n = count($t);
    $media = array_sum($t) / $n;
    $var = $n > 1 ? array_sum(array_map(fn ($x) => ($x - $media) ** 2, $t)) / ($n - 1) : 0.0;
    return ['media' => $media, 'desv' => sqrt($var), 'min' => min($t), 'max' => max($t)];
}

function medir(callable $preparar, callable $funcion, int $repeticiones = REPETICIONES): array
{
    for ($i = 0; $i < CALENTAMIENTOS; $i++) {
        $funcion(...$preparar());
    }
    $tiempos = [];
    for ($i = 0; $i < $repeticiones; $i++) {
        $args = $preparar();
        $t0 = hrtime(true);
        $funcion(...$args);
        $tiempos[] = ms($t0);
    }
    return estadisticas($tiempos);
}

// --- Trabajador: un estudiante que rinde y envia un examen de k preguntas
function trabajador(float $inicio, int $simulacroId, int $k): void
{
    mt_srand(getmypid());
    $pdo = conectar();
    while (microtime(true) < $inicio) {
        usleep(200);
    }
    $t0 = hrtime(true);
    $examen = generarExamen($pdo, TODAS, $k);
    $tShow = ms($t0);
    $respuestas = responder($examen);
    $t1 = hrtime(true);
    corregirExamen($pdo, $simulacroId, $respuestas);
    echo json_encode(['show' => $tShow, 'evaluar' => ms($t1)]);
}

function concurrencia(int $usuarios, int $simulacroId, int $k): array
{
    $inicio = microtime(true) + 1.0 + 0.05 * $usuarios;
    $procesos = [];
    for ($u = 0; $u < $usuarios; $u++) {
        $cmd = [PHP_BINARY, __FILE__, '--trabajador', (string) $inicio, (string) $simulacroId, (string) $k];
        $proc = proc_open($cmd, [1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
        $procesos[] = [$proc, $pipes];
    }
    $resultados = [];
    foreach ($procesos as [$proc, $pipes]) {
        $salida = stream_get_contents($pipes[1]);
        $error = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        proc_close($proc);
        $r = json_decode($salida, true);
        if (!$r) {
            throw new RuntimeException("Trabajador fallo: $salida $error");
        }
        $resultados[] = $r;
    }
    return $resultados;
}

if (($argv[1] ?? '') === '--trabajador') {
    trabajador((float) $argv[2], (int) $argv[3], (int) $argv[4]);
    exit(0);
}

// ---------------------------------------------------------------------------
mt_srand(42);
$simulacroId = prepararCopia();
$pdo = conectar();
$limpiar = fn () => $pdo->exec('TRUNCATE TABLE simulacro_respuestas');
$nombres = $pdo->query('SELECT id, nombre FROM materias')->fetchAll(PDO::FETCH_KEY_PAIR);
$porMateria = $pdo->query('SELECT materia_id, COUNT(*) FROM preguntas GROUP BY materia_id')->fetchAll(PDO::FETCH_KEY_PAIR);
$contar = fn (array $ms) => array_sum(array_map(fn ($m) => $porMateria[$m], $ms));
$csv = [['escenario', 'x', 'n_banco', 'k', 'paso', 'media_ms', 'desv_ms', 'min_ms', 'max_ms', 'consultas']];

// 1) Escalar k (todas las materias)
echo "1) Escalando k...\n";
$filasK = [];
foreach ([10, 25, 50, 100, 200, 500] as $k) {
    $show = medir(fn () => [$pdo, TODAS, $k], 'generarExamen');
    $evaluar = medir(function () use ($pdo, $k, $limpiar) {
        $limpiar();
        return [$pdo, $GLOBALS['simulacroId'], responder(generarExamen($pdo, TODAS, $k))];
    }, 'corregirExamen');
    $filasK[] = compact('k', 'show', 'evaluar');
    $csv[] = ['k', $k, $contar(TODAS), $k, 'show', ...array_values($show), 1];
    $csv[] = ['k', $k, $contar(TODAS), $k, 'evaluar', ...array_values($evaluar), 2 * $k + 2];
}

// 2) Escalar n (tamano del banco de las materias elegidas), k fijo = 100
echo "2) Escalando n...\n";
$filasN = [];
foreach ([[1], [1, 2], [1, 2, 4], [3, 4, 5], TODAS] as $materias) {
    $n = $contar($materias);
    $show = medir(fn () => [$pdo, $materias, 100], 'generarExamen');
    $filasN[] = ['materias' => implode(' + ', array_map(fn ($m) => $nombres[$m], $materias)), 'n' => $n, 'show' => $show];
    $csv[] = ['n', $n, $n, 100, 'show', ...array_values($show), 1];
}

// 3) Usuarios simultaneos (procesos PHP en paralelo), examen de 100 preguntas
echo "3) Usuarios simultaneos...\n";
$filasU = [];
foreach ([1, 5, 10, 25, 50] as $usuarios) {
    concurrencia(min($usuarios, 5), $simulacroId, 100); // calentamiento
    $show = $evaluar = [];
    for ($r = 0; $r < REPETICIONES_CONCURRENCIA; $r++) {
        $limpiar();
        foreach (concurrencia($usuarios, $simulacroId, 100) as $res) {
            $show[] = $res['show'];
            $evaluar[] = $res['evaluar'];
        }
    }
    $filasU[] = ['u' => $usuarios, 'show' => estadisticas($show), 'evaluar' => estadisticas($evaluar)];
    $csv[] = ['usuarios', $usuarios, $contar(TODAS), 100, 'show', ...array_values(estadisticas($show)), $usuarios];
    $csv[] = ['usuarios', $usuarios, $contar(TODAS), 100, 'evaluar', ...array_values(estadisticas($evaluar)), $usuarios * 202];
}

$version = $pdo->query('SELECT VERSION()')->fetchColumn();
$flush = $pdo->query("SELECT @@innodb_flush_log_at_trx_commit")->fetchColumn();
conectar(null)->exec('DROP DATABASE IF EXISTS ' . BD);

// --- Reporte -----------------------------------------------------------------
$f = fn (float $x) => number_format($x, 2, ',', '.');
$md = "# Mediciones del proceso actual - H1\n\n"
    . "Generado por `C:\\xampp\\php\\php.exe h1\\medir.php` el " . date('Y-m-d H:i') . ".\n\n"
    . "## Condiciones\n\n"
    . "- XAMPP local: PHP " . PHP_VERSION . ", MariaDB $version (`innodb_flush_log_at_trx_commit=$flush`), "
    . php_uname('s') . ' ' . php_uname('r') . ', ' . (getenv('PROCESSOR_IDENTIFIER') ?: php_uname('m')) . "\n"
    . "- Datos: copia de las tablas reales de `plataforma_med` (" . $contar(TODAS) . " preguntas, 5 materias)\n"
    . "- Se ejecutan las mismas consultas SQL que genera `SimulacroController` (`show` y `evaluar`); "
    . "no se incluye el arranque de Laravel ni el render de la vista, así que el tiempo real es **mayor**\n"
    . "- Protocolo: " . CALENTAMIENTOS . " calentamientos + " . REPETICIONES . " repeticiones por punto; "
    . "usuarios simultáneos: " . REPETICIONES_CONCURRENCIA . " repeticiones, procesos PHP en paralelo con arranque sincronizado\n\n"
    . "## 1. Escalando k (preguntas pedidas), todas las materias (n = " . $contar(TODAS) . ")\n\n"
    . "| k | Generar examen `show` (ms) | desv | Corregir `evaluar` (ms) | desv | Consultas en `evaluar` |\n"
    . "|---:|---:|---:|---:|---:|---:|\n";
foreach ($filasK as $r) {
    $md .= "| {$r['k']} | {$f($r['show']['media'])} | {$f($r['show']['desv'])} | {$f($r['evaluar']['media'])} | "
        . "{$f($r['evaluar']['desv'])} | " . (2 * $r['k'] + 2) . " |\n";
}
$md .= "\n## 2. Escalando n (preguntas de las materias elegidas), k = 100\n\n"
    . "| Materias | n | Generar examen `show` (ms) | desv |\n|---|---:|---:|---:|\n";
foreach ($filasN as $r) {
    $md .= "| {$r['materias']} | {$r['n']} | {$f($r['show']['media'])} | {$f($r['show']['desv'])} |\n";
}
$md .= "\n## 3. Usuarios simultáneos, examen de 100 preguntas (todas las materias)\n\n"
    . "| Usuarios | `show` media (ms) | `show` peor (ms) | `evaluar` media (ms) | `evaluar` peor (ms) | Consultas totales |\n"
    . "|---:|---:|---:|---:|---:|---:|\n";
foreach ($filasU as $r) {
    $md .= "| {$r['u']} | {$f($r['show']['media'])} | {$f($r['show']['max'])} | {$f($r['evaluar']['media'])} | "
        . "{$f($r['evaluar']['max'])} | " . ($r['u'] * 203) . " |\n";
}
file_put_contents(__DIR__ . '/mediciones.md', $md);

$salida = fopen(__DIR__ . '/mediciones.csv', 'w');
foreach ($csv as $fila) {
    fputcsv($salida, array_map(fn ($v) => is_float($v) ? round($v, 4) : $v, $fila));
}
fclose($salida);
echo $md;
