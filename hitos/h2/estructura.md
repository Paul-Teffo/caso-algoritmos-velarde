Paul Steffano Velarde Chuquimia

**<ins>H2: La estructura que elijo y por qué</ins>**

**<ins>1. Lo que elijo</ins>**

Para las dos operaciones que más hago elijo la tabla hash (el diccionario de Python). Uso dos diccionarios:

- correctas: id de la pregunta -> letra correcta. Sirve para corregir. En vez de recorrer todo el banco para encontrar una pregunta, el diccionario va directo a ella.
- por_materia: número de materia -> lista de sus preguntas. Sirve para armar el examen. En vez de mirar las n preguntas para ver cuáles son de Pediatría, voy directo a la lista de Pediatría y saco las preguntas al azar de ahí.

Los dos diccionarios se arman una sola vez, cuando se carga el banco de preguntas.

**<ins>2. Por qué una tabla hash y no otra estructura</ins>**

- En corregir y armar solo busco por clave exacta: "la pregunta 1520" o "las preguntas de la materia 4". No necesito orden, y para eso la tabla hash es lo más rápido: O(1) por búsqueda.
- Un árbol de búsqueda también funcionaría, pero cada búsqueda cuesta O(log n), y aquí no aprovecharía el orden que ofrece.
- Una lista simple obliga a recorrer todo: O(n) por búsqueda. Es lo que hace el sistema hoy.

Para ver el puesto de una nota sí hace falta orden. Ahí usaría una lista de notas ordenada con búsqueda binaria (el módulo bisect de Python): encontrar cuántas notas son mayores cuesta O(log N). Esta operación se hace una sola vez por simulacro, así que no es la que mido.

**<ins>3. Costo de las operaciones que más hago</ins>**

n = preguntas del banco, k = preguntas del examen, c = preguntas de las materias elegidas, N = notas guardadas.

| Operación | Cuántas veces la hago | Estructura | Costo O elegida | Costo O hoy (lista) |
|---|---|---|---|---|
| Corregir (buscar cada pregunta por id) | k por simulacro (hasta 100) | diccionario correctas | O(1) por búsqueda, O(k) el examen | O(n) por búsqueda, O(k · n) el examen |
| Armar el examen | 1 o más por simulacro | diccionario por_materia | O(c + k) | O(n) |
| Puesto de la nota | 1 por simulacro | lista ordenada + bisect | O(log N) para buscar | O(N) |
| Agregar una pregunta | pocas | los dos diccionarios | O(1) | O(1) |

**<ins>4. Cuándo cambiaría de opinión</ins>**

- Si el banco fuera muy chico (por ejemplo 150 preguntas), la diferencia sería de milisegundos y la lista simple alcanzaría.
- Si necesitara buscar por rangos (por ejemplo "preguntas creadas entre dos fechas"), la tabla hash no sirve porque no guarda orden, y usaría un árbol de búsqueda.
- En el sistema real esto se traduce en traer todas las respuestas correctas del examen con una sola consulta y guardarlas en un diccionario, en vez de hacer una consulta por cada respuesta.
