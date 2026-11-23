Paul Steffano Velarde Chuquimia

**<ins>H2: Inventario de los datos y las operaciones</ins>**

Mi caso es el simulador de exámenes para la residencia médica (SimulacroController, en Laravel). El proceso lento está descrito en el H1.

**<ins>1. Los datos</ins>**

| Dato | Cantidad real | Clave | Qué guarda |
|---|---|---|---|
| Preguntas | 2 877 | id | materia, enunciado, 5 opciones, respuesta correcta y justificación |
| Materias | 5 | id | nombre |
| Simulacros rendidos | 143 | id | estudiante, materias, cantidad de preguntas y nota |
| Respuestas de los simulacros | 3 145 | simulacro y pregunta | la letra que marcó el estudiante |

Preguntas por materia: Medicina Interna 1 096, Ginecoobstetricia 664, Cirugía 625, Pediatría 346 y Salud Pública 146.

**<ins>2. Las operaciones</ins>**

n = preguntas del banco, k = preguntas del examen (22 en promedio, 100 como máximo).

| Operación | Tipo | Cuándo pasa | Frecuencia |
|---|---|---|---|
| Corregir: buscar la pregunta de cada respuesta y ver si está bien | Buscar por clave (id) | Al enviar el examen | La que más se hace: k búsquedas por simulacro |
| Armar el examen: juntar las preguntas de las materias elegidas y sacar k al azar | Buscar por clave (materia) | Al abrir el simulacro y en cada recarga de la página | Muy alta: 1 o más por simulacro |
| Ver el puesto de mi nota entre todas | El siguiente o un rango (cuántas notas son mayores) | Al terminar cada simulacro | Media: 1 por simulacro |
| Agregar una pregunta | Insertar | Cuando el administrador carga preguntas | Baja |
| Borrar una pregunta | Borrar | Casi nunca | Muy baja |
| Ver mis notas de menor a mayor | Recorrer en orden | Al ver el historial | Baja |

**<ins>3. Ajuste con la clase 9</ins>**

En la clase 8 anoté todo como "buscar". Después de la clase 9 vi que hay que separar dos casos:

- Corregir y armar el examen solo buscan por clave exacta (el id de la pregunta o el número de la materia). No necesitan orden, así que alcanza con una tabla hash.
- Ver el puesto de la nota y recorrer las notas en orden sí necesitan orden. Ahí conviene tener las notas ordenadas.

Lo que más hago es corregir y armar el examen, que son justo las dos partes lentas que medí en el H1.
