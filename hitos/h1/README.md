Paul Steffano Velarde Chuquimia

**<ins>H1: El proceso lento que voy a optimizar</ins>**

**<ins>1. Descripción</ins>**

El proceso que quiero mejorar es cómo mi plataforma de preparación para la residencia médica arma y corrige los simulacros de examen (SimulacroController, hecho en Laravel).

El estudiante elige una o más materias y cuántas preguntas quiere. El sistema arma un examen de selección múltiple al azar, con 60 segundos por pregunta.

Para armarlo usa ORDER BY RAND(). Eso significa que cada vez que se carga la página, la base de datos lee todas las preguntas de las materias elegidas y las ordena al azar, aunque solo necesite unas pocas.

Al enviar el examen, o cuando se acaba el tiempo, el sistema revisa las respuestas una por una. Por cada respuesta busca la pregunta en la base de datos y guarda el resultado por separado. En total hace 2k + 2 consultas, donde k es la cantidad de preguntas.

Lo sufren los estudiantes. Hay 128 usuarios registrados y en época de examen se juntan muchos: el día con más uso tuvo 10 simulacros (mayo de 2026).

Se nota de dos formas: la pantalla del examen tarda más cuando hay muchas preguntas o materias, y cuando hay mucha gente la nota tarda en aparecer.

Los datos son 2 877 preguntas en 5 materias: Medicina Interna 1 096, Ginecoobstetricia 664, Cirugía 625, Pediatría 346 y Salud Pública 146. Cada pregunta tiene 5 opciones y una justificación.

Hasta hoy se rindieron 143 simulacros con 3 145 preguntas. En promedio se piden 22 preguntas por simulacro y como máximo 100.

**<ins>2. Lo que medí</ins>**

Medí en XAMPP local, solo las consultas (sin Laravel ni internet):

- Armar el examen tarda unos 12 ms y depende del tamaño del banco, no de k: 6 ms con 146 preguntas y 13 ms con 2 877.
- Corregir crece en línea recta con k: 141 ms para 100 preguntas y 685 ms para 500, porque cada respuesta hace 2 consultas y se guarda por separado.
- Con 50 estudiantes enviando a la vez un examen de 100 preguntas, corregir sube a 1,4 segundos en promedio (1,7 s en el peor caso) y se hacen 10 150 consultas.
- En el hosting real cada consulta además espera la red, así que los tiempos reales son mayores.

Estimación actual: armar es O(n log n) por ordenar al azar, corregir hace O(k) consultas y con U usuarios son O(U·k) consultas en total. La meta es que buscar cada pregunta cueste O(1) y que corregir use una sola consulta.

**<ins>3. Muestra de datos reales</ins>**

La saqué de la base plataforma_med con exportar_muestra.php:

- muestra_preguntas.csv: 20 preguntas reales (4 por materia) con todas sus columnas.
- muestra_materias.csv: las 5 materias.

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

**<ins>4. Mediciones</ins>**

La tabla completa está en mediciones.md y los datos crudos en mediciones.csv. Se generan con medir.php, que hace las mismas consultas que SimulacroController sobre una copia temporal de los datos reales.

Para correrlo: C:\xampp\php\php.exe hitos\h1\exportar_muestra.php y luego C:\xampp\php\php.exe hitos\h1\medir.php

**<ins>5. Otros problemas que encontré al revisar el código</ins>**

- La corrección compara una letra con un texto. La pantalla envía A a E, pero la columna respuesta guarda el texto de la opción correcta (en 2 876 de 2 877 preguntas). Con el código actual, ninguna respuesta se cuenta como correcta.
- Recargar la página cambia el examen, porque las preguntas se sortean cada vez y no se guardan.
- En la base local falta la tabla simulacro_respuestas, porque la migración de julio de 2026 no se ejecutó en local.
