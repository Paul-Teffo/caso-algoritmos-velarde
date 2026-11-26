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

Lo hice antes de revisar el código real. Supuse que el sistema sorteaba las preguntas una por una y hacía una consulta por cada pregunta y por cada respuesta. Al revisar el código encontré que usa ORDER BY RAND(), así que esta simulación no coincide con el sistema real. El análisis vigente es el de las secciones 1 a 5.

Lo que sí me dejó es la idea de cargar las preguntas una sola vez en un diccionario y corregir sin hacer una consulta por respuesta, que desarrollé en el H2. Los resultados están en [resultados.md](hitos/h1/simulacion-reconstruida/resultados.md). Para correrlo: python hitos/h1/simulacion-reconstruida/benchmark.py

---

**<ins>H2: La estructura de mi caso</ins>**

- [inventario.md](hitos/h2/inventario.md): los datos y las operaciones, y el ajuste después de la clase 9 (qué busca por clave y qué necesita orden).
- [estructura.md](hitos/h2/estructura.md): la estructura elegida (dos diccionarios), por qué, el costo de cada operación y cuándo cambiaría de opinión.
- [medicion.md](hitos/h2/medicion.md): protocolo, tabla de 4 tamaños y conclusión. Código en [simulacro.py](hitos/h2/simulacro.py), salida en [salida.txt](hitos/h2/salida.txt) y datos en [resultados.csv](hitos/h2/resultados.csv). Para correrlo: python hitos/h2/simulacro.py

**Borrador anterior del H2** ([hitos/h2/borrador](hitos/h2/borrador/))

Primera versión del H2. Usaba un árbol ordenado (SortedList) para armar el examen y para el puesto de la nota. La cambié por dos diccionarios (estructura.md), porque armar y corregir solo buscan por clave exacta y no necesitan orden. En la prueba rápida con 50 000 preguntas, corregir con el árbol tardó 0,965 ms y con el diccionario 0,015 ms.

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
3. **El salto x6 de la inserción entre 40k y 80k** está por encima del x4 teórico. Cada corrida dura más de 3 minutos y los tiempos variaron entre corridas (la tercera tardó 198 s y las dos primeras 210 s), así que lo tomo como ruido de la máquina. La tendencia cuadrática no cambia.
4. **QuickSort le gana a MergeSort** por un 25–30 % en todos los tamaños. Los dos son O(n log n), pero QuickSort ordena en el mismo arreglo y no copia datos a un buffer auxiliar, así que hace menos trabajo en cada paso. **La notación O no dice nada de las constantes, y en la práctica las constantes importan.**
5. **El sort() de Python es de 15 a 20 veces más rápido** que nuestras versiones n log n. Tiene la misma complejidad, pero está escrito en C y no pasa por el intérprete en cada comparación. En Python, lo práctico es usar siempre el sort nativo y dejar las implementaciones propias para aprender.
6. **Relación con el proyecto (simulador de exámenes):** cualquier parte del simulador que recorra o compare datos de forma cuadrática, como buscar una pregunta comparándola contra todas las demás, va a escalar igual que la inserción. Al pasar de pocas preguntas o usuarios a muchos, el tiempo se dispara. La optimización tiene que apuntar a bajar el **orden** del algoritmo, no solo a micro-mejoras.
