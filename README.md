Paul Steffano Velarde Chuquimia

**<ins>Análisis y optimización de algoritmos: simulador de exámenes</ins>**

Caso de estudio sobre un simulador de exámenes para la residencia médica. Busco las partes lentas al armar y corregir los simulacros, comparo una solución simple con una mejorada y mido cuánto cambia el tiempo.

**<ins>Cómo avanzó el caso</ins>**

1. **H1, el proceso lento:** revisé el código real (SimulacroController en Laravel) y medí en XAMPP con PHP y datos reales. Armar el examen usa ORDER BY RAND() y corregir hace 2k + 2 consultas, una por respuesta. Con 50 estudiantes a la vez, corregir tarda 1,4 s. Antes de ver el código real hice una primera simulación en Python, que quedó como material del H1.
2. **H2, la estructura:** separé las operaciones que solo buscan por clave (corregir y armar) de las que necesitan orden (el puesto de la nota). Elegí dos diccionarios y medí: con 40 000 preguntas la versión elegida es unas 700 veces más rápida que la lista y da la misma nota.
3. **H3, la estrategia:** armar al azar y corregir no se optimizan con voraz ni con dinámica, porque no hay nada que maximizar. Sí aparece una decisión: qué preguntas poner con tiempo límite (mochila 0/1). Si todas duran 60 s alcanza el voraz; si duran distinto hace falta la dinámica, que con 22 preguntas es unas 3 000 veces más rápida que la fuerza bruta.
4. **Taller, el caso como grafo:** las partes lentas no son grafos, pero el simulacro de repaso es un grafo dirigido sin ciclos (la dinámica del H3 es su camino más largo) y las preguntas que se fallan juntas forman un grafo con pesos para recomendar repaso.

**<ins>Índice del expediente</ins>**

| Entrega | Carpeta | Contenido |
|---|---|---|
| H1: El proceso lento que voy a optimizar | [hitos/h1](hitos/h1/) | Descripción del proceso real (abajo), [muestra de 20 preguntas reales](hitos/h1/muestra_preguntas.csv), [mediciones en XAMPP](hitos/h1/mediciones.md) y la [simulación reconstruida](hitos/h1/simulacion-reconstruida/) |
| H2: La estructura de mi caso | [hitos/h2](hitos/h2/) | [Inventario](hitos/h2/inventario.md), [estructura elegida](hitos/h2/estructura.md) (diccionarios), [medición](hitos/h2/medicion.md) de la versión ingenua contra la elegida y el [borrador](hitos/h2/borrador/) |
| H3: La estrategia de mi caso | [hitos/h3](hitos/h3/) | [Voraz o dinámica](hitos/h3/estrategia.md) y [comparación medida](hitos/h3/comparacion.md) de fuerza bruta contra dinámica |
| Taller: el caso como grafo | [hitos/h3/grafo.md](hitos/h3/grafo.md) | Qué partes del caso son un grafo, con sus nodos y aristas |
| Parcial 1 | [parcial1](parcial1/) | Examen parcial 1 |
| Parcial 2 | [parcial2](parcial2/) | Examen parcial 2: turnos de una clínica |
| Práctica C3 | [practica/c3](practica/c3/) | Práctica de clase 3 |
| Práctica C5 | [practica/c5](practica/c5/) | Torneo de ordenamiento: inserción, MergeSort, QuickSort y sort() (detalle abajo) |
| Práctica C10 | [practica/c10](practica/c10/) | Heaps, colas de prioridad y HeapSort |

---

**<ins>H1: El proceso lento que voy a optimizar</ins>**

**1. Descripción**

El proceso que quiero mejorar es cómo mi plataforma de preparación para la residencia médica arma y corrige los simulacros de examen (SimulacroController, hecho en Laravel).

El estudiante elige una o más materias y cuántas preguntas quiere. El sistema arma un examen de selección múltiple al azar, con 60 segundos por pregunta.

Para armarlo usa ORDER BY RAND(). Eso significa que cada vez que se carga la página, la base de datos lee todas las preguntas de las materias elegidas y las ordena al azar, aunque solo necesite unas pocas.

Al enviar el examen, o cuando se acaba el tiempo, el sistema revisa las respuestas una por una. Por cada respuesta busca la pregunta en la base de datos y guarda el resultado por separado. En total hace 2k + 2 consultas, donde k es la cantidad de preguntas.

Lo sufren los estudiantes. Hay 128 usuarios registrados y en época de examen se juntan muchos: el día con más uso tuvo 10 simulacros (mayo de 2026).

Se nota de dos formas: la pantalla del examen tarda más cuando hay muchas preguntas o materias, y cuando hay mucha gente la nota tarda en aparecer.

Los datos son 2 877 preguntas en 5 materias: Medicina Interna 1 096, Ginecoobstetricia 664, Cirugía 625, Pediatría 346 y Salud Pública 146. Cada pregunta tiene 5 opciones y una justificación.

Hasta hoy se rindieron 143 simulacros con 3 145 preguntas. En promedio se piden 22 preguntas por simulacro y como máximo 100.

**2. Lo que medí**

Medí en XAMPP local, solo las consultas (sin Laravel ni internet):

- Armar el examen tarda unos 12 ms y depende del tamaño del banco, no de k: 6 ms con 146 preguntas y 13 ms con 2 877.
- Corregir crece en línea recta con k: 141 ms para 100 preguntas y 685 ms para 500, porque cada respuesta hace 2 consultas y se guarda por separado.
- Con 50 estudiantes enviando a la vez un examen de 100 preguntas, corregir sube a 1,4 segundos en promedio (1,7 s en el peor caso) y se hacen 10 150 consultas.
- En el hosting real cada consulta además espera la red, así que los tiempos reales son mayores.

Estimación actual: armar es O(n log n) por ordenar al azar, corregir hace O(k) consultas y con U usuarios son O(U·k) consultas en total. La meta es que buscar cada pregunta cueste O(1) y que corregir use una sola consulta.

**3. Muestra de datos reales**

La saqué de la base plataforma_med con [exportar_muestra.php](hitos/h1/exportar_muestra.php):

- [muestra_preguntas.csv](hitos/h1/muestra_preguntas.csv): 20 preguntas reales (4 por materia) con todas sus columnas.
- [muestra_materias.csv](hitos/h1/muestra_materias.csv): las 5 materias.

Columnas de la tabla preguntas:

| Columna | Tipo | Contenido |
|---|---|---|
| id | bigint | Identificador |
| pregunta | varchar(255) | Enunciado |
| respuesta | varchar(255) | Texto de la opción correcta |
| opcion_a a opcion_e | varchar(255) | Las 5 opciones |
| materia_id | bigint | Materia (1 a 5) |
| justificacion | text | Explicación que se muestra al corregir |
| created_at, updated_at | timestamp | Fechas de Laravel |

**4. Mediciones**

La tabla completa está en [mediciones.md](hitos/h1/mediciones.md) y los datos crudos en [mediciones.csv](hitos/h1/mediciones.csv). Se generan con [medir.php](hitos/h1/medir.php), que hace las mismas consultas que SimulacroController sobre una copia temporal de los datos reales.

Para correrlo: C:\xampp\php\php.exe hitos\h1\exportar_muestra.php y luego C:\xampp\php\php.exe hitos\h1\medir.php

**5. Otros problemas que encontré al revisar el código**

- La corrección compara una letra con un texto. La pantalla envía A a E, pero la columna respuesta guarda el texto de la opción correcta (en 2 876 de 2 877 preguntas). Con el código actual, ninguna respuesta se cuenta como correcta.
- Recargar la página cambia el examen, porque las preguntas se sortean cada vez y no se guardan.
- En la base local falta la tabla simulacro_respuestas, porque la migración de julio de 2026 no se ejecutó en local.

**6. Primer análisis: simulación reconstruida en Python** ([hitos/h1/simulacion-reconstruida](hitos/h1/simulacion-reconstruida/))

Este análisis lo hice antes de revisar el código real del sistema. Supone un sorteo con in_array y consultas N+1 al generar el examen, pero el código real usa ORDER BY RAND(). El análisis vigente es el de las secciones 1 a 5. Lo dejo porque muestra cómo llegué a la estimación de O y la idea de la versión optimizada.

<details>
<summary>Ver el análisis completo de la simulación reconstruida</summary>

<br>

**Caso:** simulador de exámenes para la residencia médica (Laravel).
**Proceso lento:** generar el examen al inicio y corregirlo al enviarlo, sobre todo en épocas de mucho tráfico.

| Archivo | Contenido |
|---|---|
| [benchmark.py](hitos/h1/simulacion-reconstruida/benchmark.py) | Medición de las dos versiones (actual y optimizada) con el volumen supuesto |
| [resultados.md](hitos/h1/simulacion-reconstruida/resultados.md) | Tabla de mediciones que genera el script |
| [resultados.csv](hitos/h1/simulacion-reconstruida/resultados.csv) | Los mismos datos en crudo para graficar |

**6.1 El proceso supuesto**

1. El estudiante elige una o varias materias (de 5) y la cantidad de preguntas **k**.
2. El sistema arma un examen de selección múltiple con **k** preguntas al azar, sin repetir, tomadas de las materias elegidas.
3. El tiempo límite es de **3 min × k** (por ejemplo, 100 preguntas son 5 horas).
4. Al enviar el examen, o cuando se acaba el tiempo, el sistema corrige, guarda las respuestas y devuelve la **nota y la corrección**.

**Volumen supuesto:** 5 materias × 100 preguntas = **500 preguntas**, con 5 opciones cada una (2 500 opciones). El banco real resultó tener 2 877 preguntas (sección 1).

**Variables del análisis:**

| Símbolo | Significado | Rango |
|---|---|---|
| `n` | preguntas disponibles en las materias elegidas | 100 a 500 |
| `k` | preguntas que pide el estudiante | 1 a `n` |
| `U` | usuarios rindiendo a la vez en época de tráfico | decenas a cientos |

**Síntomas observados:**
- **(S1)** La pantalla de inicio tarda más cuantas más preguntas se piden.
- **(S2)** En época de tráfico, el envío tarda mucho en devolver la nota y la corrección.

**6.2 ¿Cómo se busca, ordena y recorre? (versión reconstruida)**

El código de abajo reconstruye cómo suele quedar un primer sistema en Laravel que muestra estos síntomas. benchmark.py lo replica tal cual (funciones `*_ingenuo`).

*Generar el examen: sorteo uno por uno, con rechazo y consultas N+1*

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

- **¿Uno por uno?** Sí. Cada pregunta se sortea, se busca en la lista de elegidas recorriéndola entera (in_array) y se trae de la BD por separado.
- **¿Todos contra todos?** Sí. Cada candidata se compara con todas las ya elegidas.
- **Rechazos:** cuando `k` se acerca a `n`, casi todos los sorteos caen en una pregunta repetida. Hacen falta en promedio `n·(Hₙ − Hₙ₋ₖ)` intentos (problema del coleccionista). Con `k = n = 500` son unos **3 400 sorteos**.

| Parte | Costo | Por qué |
|---|---|---|
| Sorteo sin repetir | **O(k²)** si `k ≪ n`; **O(n² log n)** si `k → n` | `k` inserciones, cada una con un in_array de O(k), más los rechazos |
| Traer preguntas y opciones | **O(k) consultas**: `1 + 2k` | N+1. Cada consulta paga la ida y vuelta de red al MySQL del hosting |

Con 500 preguntas son **1 001 consultas** solo para mostrar el examen. Esto explica el síntoma **S1**.

*Corregir al enviar: todos contra todos, con N+1 y un commit por respuesta*

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

| Parte | Costo | Por qué |
|---|---|---|
| Emparejar respuesta con pregunta | **O(k²)** | `k` respuestas × recorrido lineal de `k` preguntas |
| Buscar la opción correcta | **O(k) consultas** | N+1 |
| Guardar | **O(k) INSERT + k commits** | una transacción por fila |

*En época de tráfico*, todo lo anterior se multiplica por los usuarios simultáneos:

- **CPU:** O(U · k²)
- **BD:** **U · (1 + 4k)** consultas. Con 200 usuarios y 100 preguntas son **80 200 consultas**.
- **Pico de envíos:** si muchos empezaron a la misma hora, el tiempo (3 min × k) se les acaba **a la vez**. Todos envían en el mismo segundo y la corrección O(k²) con 2k consultas se ejecuta U veces en paralelo sobre el mismo MySQL compartido. Esto explica el síntoma **S2**.

| Paso | O actual (CPU) | Consultas BD actuales |
|---|---|---|
| Generar examen | O(k²), y O(n² log n) cuando `k → n` | 1 + 2k |
| Corregir | O(k²) | 2k (+ k commits) |
| Tráfico | O(U · k²) | U · (1 + 4k) |

En la práctica, con `n ≤ 500`, **lo que más pesa son las consultas, que crecen O(k) pero cada una es carísima**: en el hosting, una ida y vuelta a MySQL cuesta unos 0,2 a 1 ms, frente a nanosegundos de una operación en memoria. El término cuadrático de CPU domina recién cuando `k → n` (ver el salto de 400 a 500 en la tabla).

**6.3 Versión de trabajo: a dónde bajamos la O**

Idea central: **el banco de preguntas casi nunca cambia**, así que no hay que pedírselo a la BD en cada examen.

| Paso | Antes | Después | Técnica |
|---|---|---|---|
| Acceder a una pregunta y sus opciones | 2 consultas | **O(1)** en memoria | Banco en caché, indexado por `id` (tabla hash) |
| "¿Ya elegí esta pregunta?" | O(k) con in_array | **No hace falta** | Fisher–Yates parcial: no produce repetidas |
| Sortear k preguntas | O(k²) a O(n² log n) | **O(k)** | Fisher–Yates parcial, `k` intercambios y cero rechazos |
| Conocer la opción correcta | 1 consulta | **O(1)** | Mapa `pregunta_id → opcion_correcta` en caché |
| Corregir el examen | O(k²) + 2k consultas | **O(k)** + **1** consulta | Recorrido único con el mapa hash, más 1 INSERT masivo |
| Tráfico | O(U·k²), U·(1+4k) consultas | **O(U·k)**, **U** consultas | Todo lo anterior |

¿Por qué O(k) y no O(1) para el examen completo? Porque hay que entregar y corregir `k` preguntas: O(k) es el mínimo posible. Lo que baja a **O(1)** es cada operación individual: buscar una pregunta, saber si es correcta o elegir la siguiente.

*Esbozo en Laravel*

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

*Decisiones de arquitectura para el tráfico*

1. **Caché en memoria del servidor.** Con el driver file o database, cada petición deserializa el banco completo: O(n). Conviene **Redis** o **APCu**, o **Laravel Octane**, que mantiene el banco vivo entre peticiones.
2. **Guardar el examen generado** (ids en orden) en el intento (`intentos.preguntas_json`). Así recargar la página no regenera el examen y la corrección no depende del cliente.
3. **No enviar `es_correcta` al navegador.** El esbozo de arriba ya lo omite.
4. **Validar el tiempo en el servidor.** Se guarda `inicio_at` y el límite es `inicio_at + 3·k min`. No hay que confiar en el reloj del navegador.
5. **Repartir el pico de envíos.** Hay dos opciones:
   - **Autoguardado:** guardar cada respuesta al marcarla. Al enviar solo queda sumar.
   - **Cola:** devolver la nota en O(k) al instante y encolar el guardado del detalle (`dispatch(new GuardarRespuestas(...))`).

**6.4 Tabla de mediciones**

Protocolo del curso: **calentar · repetir · promediar · escalar · mismas condiciones**, con 500 preguntas. Las dos versiones usan la misma BD, los mismos índices, las mismas semillas y las mismas respuestas. Antes de medir, el script **verifica que las dos den la misma nota**.

La tabla completa, con media, desviación, cantidad de consultas y exponente empírico, está en [resultados.md](hitos/h1/simulacion-reconstruida/resultados.md). Resumen de la última corrida (medias en ms):

| Escenario | Actual | Optimizada | Mejora |
|---|---:|---:|---:|
| Generar examen, k = 100 | 2,22 ms (201 consultas) | 0,08 ms (0 consultas) | ~28× |
| Generar examen, k = 500 | 17,61 ms (1 001 consultas) | 0,40 ms (0 consultas) | ~44× |
| Corregir, k = 100 | 3,59 ms (200 consultas) | 0,36 ms (1 consulta) | ~10× |
| Corregir, k = 500 | 23,33 ms (1 000 consultas) | 0,90 ms (1 consulta) | ~26× |
| Tráfico, 200 usuarios × 100 preguntas | 1 106,6 ms (80 200 consultas) | 60,7 ms (200 consultas) | ~18× |

Lectura de la tabla:

- **Exponente empírico** (pendiente log-log entre filas): la versión actual se mantiene cerca de **1** mientras dominan las consultas, que son O(k). De 400 a 500 preguntas **salta a ~3,5**: ahí aparece el sorteo con rechazo más in_array (O(n² log n)). Esto confirma el síntoma S1: "con muchas preguntas se vuelve lento".
- **Tráfico:** las dos versiones escalan de forma lineal en U, pero la actual hace **401 veces más consultas** por usuario.
- **Esto es un piso, no un techo.** SQLite es local y no tiene red. En el hosting, cada consulta cuesta unos 0,2 a 1 ms extra. Con 0,5 ms:
  - generar un examen de 500 preguntas suma **~0,5 s** solo de red (1 001 × 0,5 ms);
  - 200 usuarios con 100 preguntas suman **~40 s** de ida y vuelta acumulada contra el mismo MySQL (80 200 × 0,5 ms);
  - la versión optimizada, con 200 consultas, suma **~0,1 s**.
- Los tiempos por debajo de 1 ms de la versión optimizada tienen ruido relativo alto. Por eso su exponente oscila entre filas: a ese nivel el costo fijo de un commit pesa más que `k`.

**6.5 Cómo reproducir**

```bash
python hitos/h1/simulacion-reconstruida/benchmark.py            # medición completa: 3 calentamientos + 10 repeticiones
python hitos/h1/simulacion-reconstruida/benchmark.py --rapido   # prueba corta
```

Solo usa la biblioteca estándar de Python 3 (incluye sqlite3). Regenera resultados.md y resultados.csv en su misma carpeta.

**6.6 Limitaciones conocidas**

- La versión "actual" **reconstruye** los patrones típicos que causan S1 y S2 (N+1, in_array dentro de un bucle, un commit por fila). Después la contrasté con el código real de Laravel (secciones 1 a 5) y no coincide: el sistema real usa ORDER BY RAND().
- El escenario de tráfico mide el **trabajo total del servidor** procesando U sesiones en serie. No simula concurrencia real (bloqueos, conexiones agotadas), que en el hosting empeora todavía más a la versión actual.
- Se mide en Python y SQLite, no en PHP y MySQL. Los valores absolutos cambian, pero la **forma** del crecimiento (la O) y la cantidad de consultas son las mismas.

</details>

---

**<ins>H2: La estructura de mi caso</ins>**

- [inventario.md](hitos/h2/inventario.md): los datos y las operaciones, y el ajuste después de la clase 9 (qué busca por clave y qué necesita orden).
- [estructura.md](hitos/h2/estructura.md): la estructura elegida (dos diccionarios), por qué, el costo de cada operación y cuándo cambiaría de opinión.
- [medicion.md](hitos/h2/medicion.md): protocolo, tabla de 4 tamaños y conclusión. Código en [simulacro.py](hitos/h2/simulacro.py), salida en [salida.txt](hitos/h2/salida.txt) y datos en [resultados.csv](hitos/h2/resultados.csv). Para correrlo: python hitos/h2/simulacro.py

**Borrador anterior del H2** ([hitos/h2/borrador](hitos/h2/borrador/))

Primera versión del H2, con árbol ordenado (SortedList) para armar el examen y para el puesto de la nota. Después elegí dos diccionarios (estructura.md), porque armar y corregir solo buscan por clave exacta.

<details>
<summary>Ver el borrador completo</summary>

<br>

**1. Inventario ajustado: ¿necesito orden o rangos, o solo buscar por clave?**

Revisé las operaciones del simulador del H1 y anoté qué necesita cada una:

| Operación | Frecuencia | ¿Qué necesita? | Estructura elegida |
|---|---|---|---|
| **A. Armar examen**: preguntas de las materias elegidas, k al azar | cada vez que se abre un simulacro | **Rango** por clave (`materia_id`) y elegir por **posición** al azar | **Árbol ordenado** (SortedList de sortedcontainers) con clave `(materia_id, id)` |
| **B. Corregir**: por cada respuesta, buscar la pregunta y comparar | k veces por envío (hasta 100) | **Solo buscar por clave** (`id`), sin orden | **Tabla hash** (dict), no un árbol |
| **C. Puesto de mi nota** (seguimiento del progreso): en qué lugar queda una nota entre todos los simulacros | cada envío | **Orden** y **rango** (cuántas notas superan la mía) | **Árbol ordenado** (SortedList) |
| Agregar pregunta al banco (admin) | poco frecuente | Mantener el orden | SortedList.add |

Conclusión del inventario: el árbol sirve donde hay **orden o rangos** (A y C). Para B, que solo busca por clave, un árbol funciona pero es más lento que un hash: O(log n) contra O(1).

Por qué sortedcontainers y no bintrees ni avl-tree:

- sortedcontainers está mantenida, es Python puro, instala sin compilar en Python 3.14 y tiene bisect_left/right (rangos) y acceso por índice (`arbol[i]`) en O(log n).
- bintrees ya no se desarrolla (su propia página en PyPI recomienda usar sortedcontainers).
- Un AVL propio enseña cómo funciona el balanceo, pero para medir conviene una librería probada.
- **Ojo:** SortedDict hereda de dict, así que `d[clave]` es una búsqueda **hash**, no un recorrido de árbol. Para medir la búsqueda en árbol de verdad usé SortedList + bisect_left.

**2. Costo de cada operación**

n = preguntas del banco, m = materias elegidas, k = preguntas del examen, N = notas guardadas.

| Operación | Ingenua (lo que hace hoy) | Costo ingenua | Adecuada | Costo adecuada |
|---|---|---|---|---|
| A. Armar examen | Filtrar todo el banco y ordenar con una clave al azar (como ORDER BY RAND()) | O(n log n) | SortedList: bisect por cada materia para su rango y k accesos por posición al azar | O(m log n + k log n), no depende de n en la práctica |
| B. Corregir | Una búsqueda recorriendo el banco por cada respuesta (como una consulta por respuesta) | O(k · n) | dict con `id → respuesta correcta` | O(k) |
| B'. Corregir con árbol (control) | SortedList de `(id, correcta)` + bisect | O(k log n) | — | — |
| C. Puesto de una nota | Lista desordenada: agregar y contar cuántas son mayores | O(N) | SortedList.add + bisect_right | O(log N) |

**3. Diseño del experimento**

- **Script:** [medir_h2.py](hitos/h2/borrador/medir_h2.py). Requiere `pip install sortedcontainers`.
- **Datos:** banco sintético con la **misma distribución real** de materias del H1 (Medicina Interna 38 %, Ginecoobstetricia 23 %, Cirugía 22 %, Pediatría 12 %, Salud Pública 5 %). La respuesta correcta es una letra A–E al azar. Semilla fija, así todas las versiones trabajan con los mismos datos.
- **Caso medido:** examen de **k = 100** (máximo real pedido) con **Pediatría + Salud Pública** (las materias elegidas son una parte chica del banco, que es justo donde ORDER BY RAND() desperdicia trabajo).
- **Tamaños de n:** 2 877 (banco real hoy) · 10 000 · 50 000 · 100 000 · 500 000.
- **Verificación antes de medir:** el examen tiene k preguntas, sin repetidas y todas de las materias elegidas; caso borde con menos preguntas que k; las tres correcciones dan la misma nota y los dos rankings el mismo puesto.
- **Protocolo:** 1 calentamiento + 3 corridas medidas con time.perf_counter(), promedio por operación en ms (20 exámenes o 200 notas por corrida para que el tiempo sea medible).
- **Qué esperaba ver:** al multiplicar n por 5, la ingenua de A y C crece unas 5 veces o más, y la de B también; la adecuada casi no cambia. En B, el árbol queda entre las dos: mucho mejor que la ingenua, pero peor que el hash.

```
cd hitos/h2/borrador
python medir_h2.py                # tamaños completos, guarda resultados.csv en esta carpeta
python medir_h2.py 2877 10000     # prueba rápida
```

**4. Resultados (prueba rápida)**

Este borrador no llegó a la corrida completa; la medición final del H2 está en medicion.md. Prueba rápida del 2026-11-19 (Python 3.14.3, Windows 11), ms por operación:

| n | armar ingenua | armar árbol | corregir ingenua | corregir árbol | corregir dict | puesto ingenua | puesto árbol |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 877 | 0,203 | 0,136 | 5,08 | 0,136 | 0,013 | 0,110 | 0,002 |
| 50 000 | 11,336 | 0,244 | 113,14 | 0,965 | 0,015 | 3,829 | 0,007 |

</details>

---

**<ins>H3: La estrategia de mi caso</ins>**

- [estrategia.md](hitos/h3/estrategia.md): por qué armar y corregir no admiten voraz ni dinámica, y la decisión que sí se optimiza (mochila 0/1), con el contraejemplo donde falla el voraz.
- [comparacion.md](hitos/h3/comparacion.md): fuerza bruta contra dinámica, protocolo, tabla de 4 tamaños y conclusión. Código en [simulacro_tiempo.py](hitos/h3/simulacro_tiempo.py), salida en [salida.txt](hitos/h3/salida.txt) y datos en [resultados.csv](hitos/h3/resultados.csv). Para correrlo: python hitos/h3/simulacro_tiempo.py
- [grafo.md](hitos/h3/grafo.md): taller del caso, qué partes se modelan como grafo y con qué nodos y aristas.

---

**<ins>Práctica C5: Torneo de ordenamiento en Python</ins>**

Código en [torneo.py](practica/c5/torneo.py), tabla en [resultados.md](practica/c5/resultados.md), las 3 corridas en [resultados.csv](practica/c5/resultados.csv) y la salida de consola en [salida_consola.txt](practica/c5/salida_consola.txt).

**Competidores**

| # | Algoritmo | Orden | Implementación |
|---|---|---|---|
| 1 | Inserción | O(n²) | propia |
| 2 | MergeSort | O(n log n) | propia (top-down con buffer auxiliar) |
| 3 | QuickSort | O(n log n) promedio | propia (partición de Hoare, pivote aleatorio) |
| 4 | list.sort() | O(n log n) | nativo de Python (Timsort escrito en C) |

**Protocolo**

- **Datos:** enteros aleatorios entre 0 y 1.000.000. Para cada tamaño se usa la misma entrada con semilla fija, así que todos los competidores ordenan exactamente el mismo arreglo.
- **Tamaños:** 10.000 · 20.000 · 40.000 · 80.000.
- **Verificación antes de medir:** cada algoritmo se prueba con casos borde (vacío, un elemento, repetidos, orden inverso) y después con el arreglo real. Su salida tiene que ser idéntica a sorted(). Si alguno falla, el torneo se detiene.
- **Calentar · 3 corridas · promediar:** hay 1 corrida de calentamiento que no se cuenta y luego 3 corridas medidas con time.perf_counter(). Cada corrida trabaja sobre una copia nueva del arreglo, y el tiempo de copiarlo no se cuenta.
- **Entorno:** Python 3.14.3, Windows 11.

Para reproducirlo: python practica/c5/torneo.py. Para una prueba rápida con tamaños propios: python practica/c5/torneo.py 1000 2000

**Tabla de tiempos (promedio, en ms)**

| Algoritmo | n = 10.000 | n = 20.000 | n = 40.000 | n = 80.000 |
|---|---:|---:|---:|---:|
| Inserción | 1.944,40 | 7.649,37 | 34.344,02 | 206.691,44 |
| MergeSort | 21,17 | 46,21 | 102,16 | 237,03 |
| QuickSort | 15,79 | 34,81 | 73,94 | 166,04 |
| sort() Python | 0,90 | 1,96 | 4,25 | 11,09 |

**Crecimiento al duplicar n**

| Algoritmo | 10k→20k | 20k→40k | 40k→80k | Teórico |
|---|---:|---:|---:|---:|
| Inserción | x3,93 | x4,49 | x6,02 | x4 |
| MergeSort | x2,18 | x2,21 | x2,32 | ≈x2,1 |
| QuickSort | x2,20 | x2,12 | x2,25 | ≈x2,1 |
| sort() Python | x2,17 | x2,16 | x2,61 | ≈x2,1 |

**Conclusiones**

1. **Se cumple la teoría.** Cada vez que n se duplica, el tiempo de la inserción se multiplica más o menos por 4, que es lo que corresponde a un algoritmo cuadrático. Los tres competidores n log n se multiplican por algo un poco mayor que 2. Las curvas tienen la forma que predice el análisis asintótico.
2. **La diferencia crece con n.** Con 10.000 elementos, la inserción es unas 120 veces más lenta que QuickSort. Con 80.000 es unas **1.250 veces** más lenta: 3,4 minutos contra 0,17 segundos. Con datos pequeños un algoritmo cuadrático puede parecer aceptable, pero al crecer los datos deja de servir.
3. **El salto x6 de la inserción entre 40k y 80k** está por encima del x4 teórico. Lo más probable es que se deba a la propia máquina: cada corrida dura más de 3 minutos, así que influyen la temperatura del CPU, otros procesos y el uso de memoria caché. La tercera corrida (198 s) fue claramente más rápida que las dos primeras (210 s), lo que confirma ese ruido. La tendencia cuadrática no cambia.
4. **QuickSort le gana a MergeSort** por un 25–30 % en todos los tamaños. Los dos son O(n log n), pero QuickSort ordena en el mismo arreglo y no copia datos a un buffer auxiliar, así que hace menos trabajo en cada paso. **La notación O no dice nada de las constantes, y en la práctica las constantes importan.**
5. **El sort() de Python es de 15 a 20 veces más rápido** que nuestras versiones n log n. Tiene la misma complejidad, pero está escrito en C y no pasa por el intérprete en cada comparación. En Python, lo práctico es usar siempre el sort nativo y dejar las implementaciones propias para aprender.
6. **Relación con el proyecto (simulador de exámenes):** cualquier parte del simulador que recorra o compare datos de forma cuadrática, como buscar una pregunta comparándola contra todas las demás, va a escalar igual que la inserción. Al pasar de pocas preguntas o usuarios a muchos, el tiempo se dispara. La optimización tiene que apuntar a bajar el **orden** del algoritmo, no solo a micro-mejoras.
