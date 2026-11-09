# H1: El proceso lento que voy a optimizar

## Descripción

El proceso que voy a optimizar es la generación y corrección de simulacros de examen en mi plataforma Laravel de preparación para la residencia médica (`SimulacroController`).
El estudiante elige una o más materias y la cantidad de preguntas, y el sistema arma un examen de selección múltiple al azar con 60 segundos por pregunta.
Para armarlo usa `inRandomOrder()`, es decir `ORDER BY RAND()`: en cada carga de la página, MySQL lee y ordena al azar todas las preguntas de las materias elegidas.
Al enviar, o cuando se acaba el tiempo, recorre las respuestas una por una: por cada una busca la pregunta en la BD y hace un INSERT con su propio commit (2k + 2 consultas).
Lo sufren los estudiantes que se preparan para la residencia: hay 128 usuarios registrados y en época de examen se juntan muchos (pico de 10 simulacros en un día, en mayo de 2026).
Los síntomas son dos: la pantalla del examen tarda más con muchas preguntas o materias, y en época de tráfico el envío demora en devolver la nota y la corrección.
Los datos son 2 877 preguntas en 5 materias (Medicina Interna 1 096, Ginecoobstetricia 664, Cirugía 625, Pediatría 346 y Salud Pública 146), cada una con 5 opciones y una justificación.
Hasta hoy se rindieron 143 simulacros con 3 145 preguntas; en promedio se piden 22 preguntas por simulacro, con un máximo de 100.
Medido hoy en XAMPP local (solo las consultas, sin Laravel ni red), generar el examen tarda unos 12 ms y depende del tamaño del banco, no de k: 6 ms con 146 preguntas y 13 ms con 2 877.
Corregir crece de forma lineal con k: 141 ms para 100 preguntas y 685 ms para 500, porque cada respuesta paga 2 consultas y un commit a disco.
Con 50 estudiantes enviando a la vez un examen de 100 preguntas, la corrección sube a 1,4 s en promedio (1,7 s en el peor caso) y suma 10 150 consultas.
En el hosting compartido cada consulta agrega además la latencia de red, así que los tiempos reales son mayores que estos.
Estimación actual: generar es O(n log n) por `ORDER BY RAND()`, corregir hace O(k) consultas con un commit cada una, y con U usuarios el total es O(U·k) consultas. La meta del mes es bajar el acceso por pregunta a O(1) con caché y corregir con una sola consulta.

## Muestra de datos reales

Exportada de la base `plataforma_med` con [`exportar_muestra.php`](exportar_muestra.php):

- [`muestra_preguntas.csv`](muestra_preguntas.csv): 20 filas reales de la tabla `preguntas` (4 por materia) con todas sus columnas.
- [`muestra_materias.csv`](muestra_materias.csv): las 5 materias (`id`, `nombre`).

Formato de la tabla `preguntas`:

| Columna | Tipo | Contenido |
|---|---|---|
| `id` | bigint | Identificador |
| `pregunta` | varchar(255) | Enunciado |
| `respuesta` | varchar(255) | **Texto** de la opción correcta |
| `opcion_a` … `opcion_e` | varchar(255) | Las 5 opciones |
| `materia_id` | bigint (FK) | Materia (1 a 5) |
| `justificacion` | text | Explicación que se muestra en la corrección |
| `created_at`, `updated_at` | timestamp | Fechas de Laravel |

## Mediciones

La tabla completa está en [`mediciones.md`](mediciones.md) (datos crudos en [`mediciones.csv`](mediciones.csv)). Se genera con [`medir.php`](medir.php), que ejecuta las mismas consultas SQL que `SimulacroController` sobre una copia temporal de los datos reales.

```
C:\xampp\php\php.exe h1\exportar_muestra.php
C:\xampp\php\php.exe h1\medir.php
```

## Hallazgos adicionales al revisar el código

- **La corrección compara una letra con un texto.** La vista envía `A`–`E`, pero `respuesta` guarda el texto de la opción correcta (2 876 de 2 877 filas). Con el código actual, ninguna respuesta se cuenta como correcta.
- **Recargar la página cambia el examen.** Las preguntas se sortean en `show()` y no se guardan, así que cada recarga genera otro examen.
- **En la base local falta la tabla `simulacro_respuestas`.** La migración de julio de 2026 no se ejecutó en local.
