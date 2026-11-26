Paul Steffano Velarde Chuquimia

**<ins>Taller del caso: ¿Mi caso se puede modelar como un grafo?</ins>**

Mi caso es el simulador de exámenes para la residencia médica (ver [H1](../../README.md), [H2](../h2/) y [H3](estrategia.md)).

Respuesta corta: **las dos partes lentas que medí (armar y corregir) no son un problema de grafos**, pero hay dos partes del caso que sí se modelan bien como grafo:

1. El simulacro de repaso con tiempo límite del H3 (la mochila) es un **grafo dirigido sin ciclos**, y la tabla de la dinámica es buscar el **camino más largo** en ese grafo.
2. Las preguntas que los estudiantes fallan juntas forman un **grafo con pesos** que sirve para recomendar qué repasar.

**<ins>1. Lo que no conviene modelar como grafo</ins>**

- **Corregir:** se busca cada pregunta por su id y se compara la letra. No hay relaciones entre preguntas, solo búsquedas por clave. Se resuelve con un diccionario (H2).
- **Armar el examen:** se toman las preguntas de las materias elegidas y se sacan k al azar. Se podría dibujar un grafo materia → pregunta, pero cada pregunta tiene una sola materia, así que es solo una agrupación (un árbol de un nivel). El diccionario por_materia del H2 ya hace eso en O(1) por materia. Un grafo no agrega nada.

**<ins>2. Grafo 1: el simulacro de repaso (mochila del H3) como camino más largo</ins>**

| Parte del grafo | En mi caso |
|---|---|
| Nodo | Un estado (i, t): "ya decidí las primeras i preguntas y usé t segundos". Es una casilla de la tabla del H3. |
| Arista "no meterla" | De (i-1, t) a (i, t), con peso 0. |
| Arista "meterla" | De (i-1, t - tiempo) a (i, t), con peso = valor de repaso de la pregunta. Solo existe si la pregunta cabe. |
| Dirección | Siempre de i-1 a i, así que **no hay ciclos** (es un DAG). |
| Lo que busco | El camino de **mayor peso** que termina en (n, T). |

Ejemplo con el contraejemplo del H3 (límite de 120 s; preguntas de 70 s/8, 60 s/6 y 60 s/6):

```
(0,0) --no 0--> (1,0) --mete 1, +6--> (2,60) --mete 2, +6--> (3,120)   total 12  (lo mejor)
(0,50) --mete 0, +8--> (1,120) --no 1--> (2,120) --no 2--> (3,120)     total 8   (lo que hace el voraz)
```

El voraz toma la arista más pesada del primer paso (+8) y después ya no le queda camino bueno. El camino más largo encuentra el de 12.

Tamaño del grafo: (n + 1)·(T + 1) nodos y como máximo 2·n·(T + 1) aristas. En el ejemplo son 4 · 121 = 484 nodos. Recorrer un DAG en orden cuesta O(nodos + aristas) = **O(n · T)**, que es exactamente el costo de la dinámica del H3. O sea, llenar la tabla y buscar el camino más largo en este grafo son lo mismo.

En el ejemplo el camino más largo vale 12, lo mismo que da la tabla de la dinámica en [salida.txt](salida.txt).

**<ins>3. Grafo 2: preguntas que se fallan juntas</ins>**

Esto sirve para el seguimiento del progreso: si un estudiante falla una pregunta, recomendarle las que otros estudiantes también fallaron junto con ella.

| Parte del grafo | En mi caso |
|---|---|
| Nodo | Una pregunta del banco (2 877 hoy). |
| Arista | Entre las preguntas p y q si al menos un estudiante falló las dos en el mismo simulacro. No tiene dirección. |
| Peso | Cuántos simulacros fallaron p y q juntas. |
| De dónde salen los datos | De la tabla simulacro_respuestas (3 145 respuestas en 143 simulacros). |

Qué se puede hacer con él:

- **Recomendar repaso:** los vecinos de una pregunta fallada, ordenados por peso. Con una lista de adyacencia esto cuesta O(grado de la pregunta), no O(n).
- **Encontrar temas débiles:** los componentes conexos (con BFS o DFS) agrupan preguntas que se fallan juntas, aunque sean de materias distintas. Cuesta O(V + E).

Cómo guardarlo: como **lista de adyacencia** en un diccionario de diccionarios (pregunta → {vecina: peso}), que es la misma idea de tabla hash del H2. Una matriz de 2 877 × 2 877 tendría más de 8 millones de casillas, casi todas en 0, porque cada simulacro toca pocas preguntas.

**Antes de usarlo hay que arreglar la corrección** ([H1](../../README.md), sección 5): hoy se compara la letra que manda la pantalla con el texto de la respuesta, así que ninguna respuesta sale correcta y todas parecerían "falladas". Con ese error el grafo tendría aristas entre todas las preguntas de cada simulacro y no diría nada.

**<ins>4. Conclusión</ins>**

| Parte del caso | ¿Grafo? | Nodos | Aristas | Algoritmo |
|---|---|---|---|---|
| Corregir | No | - | - | Diccionario (H2) |
| Armar el examen | No sirve | - | - | Diccionario por materia (H2) |
| Simulacro de repaso con tiempo límite | Sí, DAG | Estados (i, t) | Meter o no meter la pregunta, con peso = valor | Camino más largo en DAG, O(n · T) = dinámica del H3 |
| Recomendar qué repasar | Sí, con pesos | Preguntas | Falladas juntas, peso = veces | Vecinos por peso y componentes conexos con BFS, O(V + E) |

Sí se puede modelar como grafo, pero no las partes lentas del H1. El grafo aparece cuando el sistema tiene que **decidir** (qué preguntas poner) o **relacionar** preguntas entre sí (cuáles se fallan juntas). El primer grafo no cambia el costo, solo es otra forma de ver la dinámica del H3. El segundo sería una función nueva, y depende de corregir primero el error de la letra contra el texto.
