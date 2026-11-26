Paul Steffano Velarde Chuquimia

**<ins>H2: Medición de la versión ingenua y la elegida</ins>**

**<ins>1. El problema que medí</ins>**

Atender un simulacro completo: armar un examen de 100 preguntas de Pediatría y Salud Pública y corregirlo. Es el proceso lento del H1.

- Versión ingenua: todo en una lista. Para armar, recorre todo el banco y mezcla las preguntas. Para corregir, recorre el banco por cada respuesta.
- Versión elegida: dos diccionarios. Para armar, va directo a la lista de cada materia. Para corregir, busca cada pregunta directo por su id.

El código está en simulacro.py. La salida completa está en salida.txt y los datos en resultados.csv. Para correrlo: python simulacro.py

**<ins>2. Protocolo</ins>**

- Datos: banco generado con semilla fija y con la misma proporción de materias que el banco real.
- Antes de medir revisé que las dos versiones den lo mismo: exámenes de 100 preguntas sin repetir y de las materias correctas, y la misma nota en 50 exámenes.
- Medición: 1 corrida para calentar, 3 corridas medidas y el promedio. Cada corrida atiende 50 simulacros y anoto el tiempo de uno.
- Tamaños: n = 5 000, 10 000, 20 000 y 40 000 (n, 2n, 4n y 8n).
- Equipo: Python 3.14.3 en Windows 11, el 22 de noviembre de 2026.

**<ins>3. Resultados</ins>**

| n | Ingenua (ms) | Veces más | Elegida (ms) | Veces más |
|---|---|---|---|---|
| 5 000 | 8,031 | - | 0,0699 | - |
| 10 000 | 19,173 | 2,39 | 0,0723 | 1,04 |
| 20 000 | 37,526 | 1,96 | 0,0825 | 1,14 |
| 40 000 | 65,133 | 1,74 | 0,0917 | 1,11 |

Detalle de cada operación por separado (ms por simulacro):

| n | Armar ingenua | Armar elegida | Corregir ingenua | Corregir elegida |
|---|---|---|---|---|
| 5 000 | 0,449 | 0,0297 | 7,888 | 0,0053 |
| 10 000 | 0,948 | 0,0328 | 15,572 | 0,0052 |
| 20 000 | 1,869 | 0,0333 | 28,311 | 0,0052 |
| 40 000 | 3,968 | 0,0473 | 60,300 | 0,0054 |

**<ins>4. Conclusión</ins>**

La versión ingenua se parece a O(n): cada vez que se duplica n, el tiempo se multiplica más o menos por 2 (entre 1,74 y 2,39). Casi todo el tiempo se va en corregir, porque busca cada respuesta recorriendo el banco.

La versión elegida casi no crece (entre 1,04 y 1,14), porque corregir con el diccionario no depende de n. Con 40 000 preguntas es unas 700 veces más rápida que la ingenua y da la misma nota.

Sobre el ruido: la versión elegida tarda menos de 0,1 ms, y a ese nivel cualquier cosa que haga Windows en el fondo cambia el resultado. Por eso sus razones no son exactamente 1. Por la misma razón la ingenua no da exactamente 2. Además, los datos están en memoria; en el servidor real cada consulta también espera a la base de datos y a la red, así que la diferencia real sería todavía mayor.
