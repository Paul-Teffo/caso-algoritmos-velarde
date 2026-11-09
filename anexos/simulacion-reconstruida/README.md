# Anexo: simulación reconstruida (primer análisis)

> **Nota:** este análisis se hizo antes de revisar el código real del sistema. Supone un sorteo con `in_array` y consultas N+1 al generar el examen, pero el código real usa `ORDER BY RAND()`. El análisis vigente está en [`h1/README.md`](../../h1/README.md). Este script se ejecuta con `python anexos/simulacion-reconstruida/benchmark.py`.

**Caso:** simulador de exámenes para la residencia médica (Laravel).
**Proceso lento:** generar el examen al inicio y corregirlo al enviarlo, sobre todo en épocas de mucho tráfico.

| Archivo | Contenido |
|---|---|
| [`README.md`](README.md) | Este análisis: el proceso, su O actual con el porqué, y la versión de trabajo |
| [`benchmark.py`](benchmark.py) | Medición de las dos versiones (actual y optimizada) con el volumen real |
| [`resultados.md`](resultados.md) | **Tabla de mediciones** que genera el script |
| [`resultados.csv`](resultados.csv) | Los mismos datos en crudo para graficar |

---

## 1. El proceso

1. El estudiante elige una o varias materias (de 5) y la cantidad de preguntas **k**.
2. El sistema arma un examen de selección múltiple con **k** preguntas al azar, sin repetir, tomadas de las materias elegidas.
3. El tiempo límite es de **3 min × k** (por ejemplo, 100 preguntas son 5 horas).
4. Al enviar el examen, o cuando se acaba el tiempo, el sistema corrige, guarda las respuestas y devuelve la **nota y la corrección**.

**Volumen real:** 5 materias × 100 preguntas = **500 preguntas**, con 5 opciones cada una (2 500 opciones).

**Variables del análisis:**

| Símbolo | Significado | Rango real |
|---|---|---|
| `n` | preguntas disponibles en las materias elegidas | 100 a 500 |
| `k` | preguntas que pide el estudiante | 1 a `n` |
| `U` | usuarios rindiendo a la vez en época de tráfico | decenas a cientos |

**Síntomas observados:**
- **(S1)** La pantalla de inicio tarda más cuantas más preguntas se piden.
- **(S2)** En época de tráfico, el envío tarda mucho en devolver la nota y la corrección.

---

## 2. ¿Cómo se busca, ordena y recorre hoy?

> El código de abajo reconstruye cómo suele quedar un primer sistema en Laravel que muestra estos síntomas. `benchmark.py` lo replica tal cual (funciones `*_ingenuo`). **Si tu código real difiere, ajusta las funciones `*_ingenuo` y vuelve a medir.**

### 2.1 Generar el examen: sorteo uno por uno, con rechazo y consultas N+1

```php
$ids = Pregunta::whereIn('materia_id', $materias)->pluck('id')->toArray();   // 1 consulta
$elegidas = [];
while (count($elegidas) < $cantidad) {
    $id = $ids[array_rand($ids)];
    if (!in_array($id, $elegidas)) {          // búsqueda lineal en un array: O(k)
        $elegidas[] = $id;
    }
}
foreach ($elegidas as $id) {
    $pregunta = Pregunta::find($id);           // 1 consulta por pregunta
    $opciones = $pregunta->opciones;           // otra consulta por pregunta (N+1)
}
```

- **¿Uno por uno?** Sí. Cada pregunta se sortea, se busca en la lista de elegidas recorriéndola entera (`in_array`) y se trae de la BD por separado.
- **¿Todos contra todos?** Sí. Cada candidata se compara con todas las ya elegidas.
- **Rechazos:** cuando `k` se acerca a `n`, casi todos los sorteos caen en una pregunta repetida. Hacen falta en promedio `n·(Hₙ − Hₙ₋ₖ)` intentos (problema del coleccionista). Con `k = n = 500` son unos **3 400 sorteos**.

**O actual de la generación:**

| Parte | Costo | Por qué |
|---|---|---|
| Sorteo sin repetir | **O(k²)** si `k ≪ n`; **O(n² log n)** si `k → n` | `k` inserciones, cada una con un `in_array` de O(k), más los rechazos |
| Traer preguntas y opciones | **O(k) consultas**: `1 + 2k` | N+1. Cada consulta paga la ida y vuelta de red al MySQL del hosting |

Con 500 preguntas son **1 001 consultas** solo para mostrar el examen. Esto explica el síntoma **S1**.

### 2.2 Corregir al enviar: todos contra todos, con N+1 y un commit por respuesta

```php
foreach ($request->respuestas as $preguntaId => $opcionId) {
    foreach ($examen as $p) {                          // busca la pregunta recorriendo el examen: O(k)
        if ($p->id == $preguntaId) { $pregunta = $p; break; }
    }
    $correcta = Opcion::where('pregunta_id', $preguntaId)
                      ->where('es_correcta', 1)->first();   // 1 consulta por respuesta
    Respuesta::create([...]);                                // 1 INSERT + commit por respuesta
}
```

**O actual de la corrección:**

| Parte | Costo | Por qué |
|---|---|---|
| Emparejar respuesta con pregunta | **O(k²)** | `k` respuestas × recorrido lineal de `k` preguntas |
| Buscar la opción correcta | **O(k) consultas** | N+1 |
| Guardar | **O(k) INSERT + k commits** | una transacción por fila |

### 2.3 En época de tráfico

Todo lo anterior se multiplica por los usuarios simultáneos:

- **CPU:** O(U · k²)
- **BD:** **U · (1 + 4k)** consultas. Con 200 usuarios y 100 preguntas son **80 200 consultas**.
- **Pico de envíos:** si muchos empezaron a la misma hora, el tiempo (3 min × k) se les acaba **a la vez**. Todos envían en el mismo segundo y la corrección O(k²) con 2k consultas se ejecuta U veces en paralelo sobre el mismo MySQL compartido. Esto explica el síntoma **S2**.

### 2.4 Resumen de la estimación

| Paso | O actual (CPU) | Consultas BD actuales |
|---|---|---|
| Generar examen | O(k²), y O(n² log n) cuando `k → n` | 1 + 2k |
| Corregir | O(k²) | 2k (+ k commits) |
| Tráfico | O(U · k²) | U · (1 + 4k) |

En la práctica, con el volumen real (`n ≤ 500`), **lo que más pesa son las consultas, que crecen O(k) pero cada una es carísima**: en el hosting, una ida y vuelta a MySQL cuesta unos 0,2 a 1 ms, frente a nanosegundos de una operación en memoria. El término cuadrático de CPU domina recién cuando `k → n` (ver el salto de 400 a 500 en la tabla).

---

## 3. Versión de trabajo: a dónde bajamos la O

Idea central: **el banco de preguntas casi nunca cambia**, así que no hay que pedírselo a la BD en cada examen.

| Paso | Antes | Después | Técnica |
|---|---|---|---|
| Acceder a una pregunta y sus opciones | 2 consultas | **O(1)** en memoria | Banco en caché, indexado por `id` (tabla hash) |
| "¿Ya elegí esta pregunta?" | O(k) con `in_array` | **No hace falta** | Fisher–Yates parcial: no produce repetidas |
| Sortear k preguntas | O(k²) a O(n² log n) | **O(k)** | Fisher–Yates parcial, `k` intercambios y cero rechazos |
| Conocer la opción correcta | 1 consulta | **O(1)** | Mapa `pregunta_id → opcion_correcta` en caché |
| Corregir el examen | O(k²) + 2k consultas | **O(k)** + **1** consulta | Recorrido único con el mapa hash, más 1 INSERT masivo |
| Tráfico | O(U·k²), U·(1+4k) consultas | **O(U·k)**, **U** consultas | Todo lo anterior |

> **¿Por qué O(k) y no O(1) para el examen completo?** Porque hay que entregar y corregir `k` preguntas: O(k) es el mínimo posible. Lo que baja a **O(1)** es cada operación individual: buscar una pregunta, saber si es correcta o elegir la siguiente.

### 3.1 Esbozo en Laravel

```php
// app/Services/BancoPreguntas.php
class BancoPreguntas
{
    public function banco(): array
    {
        // 2 consultas, una sola vez. Se invalida con Cache::forget('banco_preguntas')
        // desde un Observer cuando el admin edita preguntas u opciones.
        return Cache::rememberForever('banco_preguntas', function () {
            $preguntas = Pregunta::with('opciones:id,pregunta_id,texto,es_correcta')
                ->get(['id', 'materia_id', 'enunciado']);
            $porId = $idsPorMateria = $correcta = [];
            foreach ($preguntas as $p) {
                $porId[$p->id] = [
                    'id' => $p->id,
                    'enunciado' => $p->enunciado,
                    'opciones' => $p->opciones->map->only(['id', 'texto'])->all(),  // sin es_correcta
                ];
                $idsPorMateria[$p->materia_id][] = $p->id;
                $correcta[$p->id] = $p->opciones->firstWhere('es_correcta', 1)->id;
            }
            return compact('porId', 'idsPorMateria', 'correcta');
        });
    }

    public function generar(array $materias, int $k): array
    {
        $b = $this->banco();
        $pool = array_merge(...array_map(fn ($m) => $b['idsPorMateria'][$m], $materias));
        $n = count($pool);
        for ($i = 0; $i < $k; $i++) {                 // Fisher–Yates parcial: O(k)
            $j = random_int($i, $n - 1);
            [$pool[$i], $pool[$j]] = [$pool[$j], $pool[$i]];
        }
        return array_map(fn ($id) => $b['porId'][$id], array_slice($pool, 0, $k));
    }

    public function corregir(int $intentoId, array $respuestas): array
    {
        $correcta = $this->banco()['correcta'];
        $filas = [];
        $nota = 0;
        foreach ($respuestas as $preguntaId => $opcionId) {     // O(k), O(1) por respuesta
            $ok = ($correcta[$preguntaId] ?? null) === (int) $opcionId;
            $nota += $ok;
            $filas[] = ['intento_id' => $intentoId, 'pregunta_id' => $preguntaId,
                        'opcion_id' => $opcionId, 'correcta' => $ok];
        }
        Respuesta::insert($filas);                               // 1 consulta, 1 transacción
        return ['nota' => $nota, 'total' => count($respuestas)];
    }
}
```

### 3.2 Decisiones de arquitectura para el tráfico

1. **Caché en memoria del servidor.** Con el driver `file` o `database`, cada petición deserializa el banco completo: O(n), con `n = 500` fijo. Conviene **Redis** o **APCu**, o **Laravel Octane**, que mantiene el banco vivo entre peticiones.
2. **Guardar el examen generado** (ids en orden) en el intento (`intentos.preguntas_json`). Así recargar la página no regenera el examen y la corrección no depende del cliente.
3. **No enviar `es_correcta` al navegador.** El esbozo de arriba ya lo omite.
4. **Validar el tiempo en el servidor.** Se guarda `inicio_at` y el límite es `inicio_at + 3·k min`. No hay que confiar en el reloj del navegador.
5. **Repartir el pico de envíos.** Hay dos opciones:
   - **Autoguardado:** guardar cada respuesta al marcarla. Al enviar solo queda sumar.
   - **Cola:** devolver la nota en O(k) al instante y encolar el guardado del detalle (`dispatch(new GuardarRespuestas(...))`).

---

## 4. Tabla de mediciones

Protocolo del curso: **calentar · repetir · promediar · escalar · mismas condiciones**, con el **volumen real** (500 preguntas). Las dos versiones usan la misma BD, los mismos índices, las mismas semillas y las mismas respuestas. Antes de medir, el script **verifica que las dos den la misma nota**.

La tabla completa, con media, desviación, cantidad de consultas y exponente empírico, está en **[`resultados.md`](resultados.md)**. Resumen de la última corrida (medias en ms):

| Escenario | Actual | Optimizada | Mejora |
|---|---:|---:|---:|
| Generar examen, k = 100 | 2,22 ms (201 consultas) | 0,08 ms (0 consultas) | ~28× |
| Generar examen, k = 500 | 17,61 ms (1 001 consultas) | 0,40 ms (0 consultas) | ~44× |
| Corregir, k = 100 | 3,59 ms (200 consultas) | 0,36 ms (1 consulta) | ~10× |
| Corregir, k = 500 | 23,33 ms (1 000 consultas) | 0,90 ms (1 consulta) | ~26× |
| Tráfico, 200 usuarios × 100 preguntas | 1 106,6 ms (80 200 consultas) | 60,7 ms (200 consultas) | ~18× |

### Lectura de la tabla

- **Exponente empírico** (pendiente log-log entre filas): la versión actual se mantiene cerca de **1** mientras dominan las consultas, que son O(k). De 400 a 500 preguntas **salta a ~3,5**: ahí aparece el sorteo con rechazo más `in_array` (O(n² log n)). Esto confirma el síntoma S1: "con muchas preguntas se vuelve lento".
- **Tráfico:** las dos versiones escalan de forma lineal en U, pero la actual hace **401 veces más consultas** por usuario.
- **Esto es un piso, no un techo.** SQLite es local y no tiene red. En el hosting, cada consulta cuesta unos 0,2 a 1 ms extra. Con 0,5 ms:
  - generar un examen de 500 preguntas suma **~0,5 s** solo de red (1 001 × 0,5 ms);
  - 200 usuarios con 100 preguntas suman **~40 s** de ida y vuelta acumulada contra el mismo MySQL (80 200 × 0,5 ms).
  - La versión optimizada, con 200 consultas, suma **~0,1 s**.
- Los tiempos por debajo de 1 ms de la versión optimizada tienen ruido relativo alto. Por eso su exponente oscila entre filas: a ese nivel el costo fijo de un commit pesa más que `k`.

---

## 5. Cómo reproducir

```bash
python h1/benchmark.py            # medición completa: 3 calentamientos + 10 repeticiones
python h1/benchmark.py --rapido   # prueba corta
```

Solo usa la biblioteca estándar de Python 3 (incluye `sqlite3`). Regenera `h1/resultados.md` y `h1/resultados.csv`.

## 6. Limitaciones conocidas

- La versión "actual" **reconstruye** los patrones típicos que causan S1 y S2 (N+1, `in_array` dentro de un bucle, un commit por fila). Antes de la entrega final hay que contrastarla con el código real de Laravel.
- El escenario de tráfico mide el **trabajo total del servidor** procesando U sesiones en serie. No simula concurrencia real (bloqueos, conexiones agotadas), que en el hosting empeora todavía más a la versión actual.
- Se mide en Python y SQLite, no en PHP y MySQL. Los valores absolutos cambian, pero la **forma** del crecimiento (la O) y la cantidad de consultas son las mismas.
