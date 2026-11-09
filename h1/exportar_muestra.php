<?php
// H1 - Exporta 20 filas reales de la tabla `preguntas` (4 por materia) con su formato verdadero.
// Uso: C:\xampp\php\php.exe h1\exportar_muestra.php
declare(strict_types=1);

$pdo = new PDO('mysql:host=127.0.0.1;port=3306;dbname=plataforma_med;charset=utf8mb4', 'root', '', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$filas = $pdo->query(
    'SELECT p.* FROM preguntas p
     WHERE (SELECT COUNT(*) FROM preguntas q WHERE q.materia_id = p.materia_id AND q.id < p.id) < 4
     ORDER BY p.materia_id, p.id'
)->fetchAll(PDO::FETCH_ASSOC);

$salida = fopen(__DIR__ . '/muestra_preguntas.csv', 'w');
fputcsv($salida, array_keys($filas[0]));
foreach ($filas as $fila) {
    fputcsv($salida, $fila);
}
fclose($salida);

$materias = $pdo->query('SELECT id, nombre FROM materias ORDER BY id')->fetchAll(PDO::FETCH_ASSOC);
$salida = fopen(__DIR__ . '/muestra_materias.csv', 'w');
fputcsv($salida, ['id', 'nombre']);
foreach ($materias as $m) {
    fputcsv($salida, $m);
}
fclose($salida);

echo count($filas) . " filas exportadas a h1/muestra_preguntas.csv\n";
