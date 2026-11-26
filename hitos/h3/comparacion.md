Paul Steffano Velarde Chuquimia

**<ins>H3: Comparación medida. Fuerza bruta contra programación dinámica</ins>**

**<ins>1. El problema</ins>**

Es el simulacro de repaso con tiempo límite explicado en estrategia.md: elegir las preguntas que den el mayor valor de repaso sin pasarse del tiempo (mochila 0/1).

- Fuerza bruta: prueba todas las combinaciones de preguntas y se queda con la mejor que entra en el tiempo. Costo O(n · 2^n).
- Programación dinámica: llena la tabla de la mochila, donde cada casilla es el mejor valor con las primeras i preguntas y t segundos. Costo O(n · T).
- Voraz: lo incluyo solo para comparar. Ordena por valor por segundo y mete lo que cabe.

El código está en simulacro_tiempo.py. La salida completa está en salida.txt y los datos en resultados.csv. Para correrlo: python simulacro_tiempo.py

**<ins>2. Protocolo</ins>**

- Datos: preguntas generadas al azar con semilla fija. Cada pregunta dura entre 50 y 130 segundos, según la estimación de estrategia.md, y tiene un valor de 1 a 10. El límite es la mitad del tiempo total, para que no entren todas.
- Mismo resultado: antes de medir, el programa comprueba que la fuerza bruta y la dinámica den el mismo valor. También lo comprobé con 300 grupos de 12 preguntas al azar: coincidieron las 300 veces.
- Medición: 1 corrida para calentar, 3 corridas medidas y el promedio.
- Tamaños: 16, 18, 20 y 22 preguntas. Cada 2 preguntas más hay 4 veces más combinaciones.
- Equipo: Python 3.14.3 en Windows 11, el 22 de noviembre de 2026.

**<ins>3. Resultados</ins>**

| n | Límite (s) | Fuerza bruta (ms) | Veces más | Dinámica (ms) | Veces más | Mejor valor | Valor del voraz |
|---|---|---|---|---|---|---|---|
| 16 | 787 | 103,9 | - | 1,79 | - | 65 | 65 |
| 18 | 925 | 469,6 | 4,5 | 2,44 | 1,4 | 81 | 80 |
| 20 | 1017 | 2 103,1 | 4,5 | 2,96 | 1,2 | 77 | 76 |
| 22 | 970 | 9 155,0 | 4,4 | 2,97 | 1,0 | 100 | 100 |

**<ins>4. Conclusión</ins>**

La fuerza bruta crece como O(n · 2^n): cada 2 preguntas más tarda unas 4,5 veces más (4 por las combinaciones y un poco más porque cada combinación revisa más preguntas). Con 22 preguntas ya tarda 9 segundos, y con 30 tardaría casi una hora.

La dinámica crece como O(n · T). Aquí el límite T casi no cambia entre filas, así que su tiempo sube poco (entre 1,0 y 1,4 veces). Con 22 preguntas es unas 3 000 veces más rápida y da el mismo resultado.

El voraz es el más rápido, pero no siempre acierta: con 18 y 20 preguntas dio 1 punto menos que lo mejor. Eso confirma el contraejemplo de estrategia.md.

Sobre el ruido: los tiempos de la dinámica son de 2 a 3 ms, y a ese nivel lo que hace Windows en el fondo cambia un poco el resultado. Por eso sus razones no siguen un patrón exacto. Los tiempos de la fuerza bruta son mucho más grandes, por eso sus razones salen muy parejas.
