Paul Steffano Velarde Chuquimia

**<ins>H3: La estrategia de mi caso. ¿Voraz o dinámica?</ins>**

Mi caso es el simulador de exámenes para la residencia médica (ver H1 y H2).

**<ins>1. Lo que el sistema hace hoy no se puede optimizar con voraz ni con dinámica</ins>**

Un algoritmo voraz o una programación dinámica sirven cuando hay que tomar decisiones para conseguir el mejor resultado posible (el máximo o el mínimo de algo). Las dos operaciones de hoy no son así:

- Armar el examen: elige preguntas al azar. No hay un examen "mejor" que otro, así que no hay nada que maximizar.
- Corregir: compara las respuestas y suma. Solo hay un resultado posible, la nota. Es un cálculo, no una decisión.

Por eso estas dos operaciones se mejoran con estructuras de datos (como hice en el H2), no con voraz ni con dinámica.

**<ins>2. La decisión de mi caso que sí se puede optimizar</ins>**

Hay una decisión que se repite en cada simulacro: qué preguntas poner cuando el tiempo es limitado. Hoy se eligen al azar, pero en un simulacro de repaso conviene elegir bien.

- Cada pregunta tiene un tiempo (los segundos que tarda el estudiante en resolverla) y un valor de repaso de 1 a 10. El sistema hoy no guarda ese valor: es una propuesta mía (por ejemplo, más alto si el estudiante ya la falló antes).
- El estudiante tiene un tiempo límite.
- Objetivo: lograr el mayor valor total sin pasarse del tiempo. Cada pregunta entra entera o no entra.

Este es el problema de la mochila 0/1: el tiempo es el "peso" y el valor de repaso es el "valor".

¿Todas las preguntas tardan lo mismo? No. En las 20 preguntas reales del H1, entre enunciado y opciones hay de 93 a 399 caracteres, así que algunas son unas cuatro veces más largas que otras. No medí cuánto tarda cada una: supongo que una pregunta corta toma unos 50 segundos y un caso clínico largo unos 130. Hoy el sistema le da 60 segundos a todas.

**<ins>3. Si todas las preguntas duran 60 segundos (como hoy): sirve el voraz</ins>**

Si todas duran lo mismo, el límite de tiempo equivale a decir "como máximo k preguntas". Lo mejor es tomar las k de mayor valor, que es justo lo que hace el voraz.

Por qué siempre acierta: supongamos una buena solución que deja afuera la pregunta de mayor valor y usa otra de menos valor. Si las cambio, el tiempo es el mismo (las dos duran 60 s) y el valor sube o queda igual. Entonces elegir siempre la de mayor valor nunca empeora el resultado.

Lo comprobé con 300 grupos de preguntas al azar con 60 segundos fijos: el voraz dio el mejor resultado las 300 veces.

**<ins>4. Si cada pregunta dura distinto (lo real): el voraz falla y sirve la dinámica</ins>**

Contraejemplo con un límite de 120 segundos:

| Pregunta | Tiempo | Valor | Valor por segundo |
|---|---|---|---|
| 0 (caso clínico largo) | 70 s | 8 | 0,114 |
| 1 (pregunta corta) | 60 s | 6 | 0,100 |
| 2 (pregunta corta) | 60 s | 6 | 0,100 |

- El voraz elige primero la de mayor valor por segundo, la pregunta 0. Le sobran 50 segundos y ya no entra ninguna de 60. Resultado: 8.
- Lo mejor es elegir la 1 y la 2, que suman 120 segundos justos. Resultado: 12.

El voraz falla porque toma la decisión que parece mejor en ese momento y no puede volver atrás, aunque deje tiempo sin usar. Con 300 grupos de preguntas al azar con tiempos distintos, el voraz dio menos que lo mejor 71 veces (24 %).

La programación dinámica sí sirve, porque el problema cumple sus dos condiciones:

- Subestructura óptima: si la mejor solución incluye una pregunta, el resto tiene que ser la mejor solución para las demás preguntas con el tiempo que sobra.
- Subproblemas que se repiten: al probar combinaciones se llega muchas veces a la misma situación (las mismas preguntas por revisar y el mismo tiempo libre). La dinámica la calcula una sola vez y la guarda en una tabla.

La tabla funciona así: tabla[i][t] es el mejor valor usando las primeras i preguntas con t segundos. Para cada pregunta hay dos opciones y se elige la mejor:

- No meterla: tabla[i-1][t]
- Meterla, si cabe: tabla[i-1][t - tiempo de la pregunta] + valor de la pregunta

**<ins>5. Costos</ins>**

| Estrategia | Costo | ¿Da el mejor resultado? |
|---|---|---|
| Fuerza bruta (probar todas las combinaciones) | O(n · 2^n) | Sí |
| Voraz (valor por segundo) | O(n log n) | Solo si todas las preguntas duran lo mismo |
| Dinámica (tabla) | O(n · T), T = límite en segundos | Sí |

**<ins>6. Conclusión</ins>**

- En lo que hace hoy el sistema (armar al azar y corregir) no sirve ni el voraz ni la dinámica, porque no hay nada que optimizar.
- Al elegir qué preguntas poner en un simulacro con tiempo límite: si todas duran 60 segundos, como hoy, el voraz es suficiente y da el mejor resultado.
- Si cada pregunta dura distinto, como pasa en la realidad, el voraz puede equivocarse (8 en vez de 12). Ahí hay que usar programación dinámica, que siempre da el mejor resultado y es mucho más rápida que probar todas las combinaciones.

La comparación medida está en comparacion.md.
