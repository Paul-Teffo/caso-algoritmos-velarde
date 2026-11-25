# Paul Steffano Velarde Chuquimia

# I1 · Analizar y elegir (Variante B: compras de una escuela)

El problema es similar al de la mochila 0/1: cada útil tiene un costo y una utilidad, y tenemos un presupuesto que no podemos superar.

## a) Costo de CompradorIngenuo.Elegir

**O(2^n · n)**

- Se generan todas las combinaciones posibles de útiles. Como cada uno puede comprarse o no, existen 2^n combinaciones.
- Para cada combinación se revisan los n útiles para sumar sus costos y utilidades.
- Por eso, el trabajo total es 2^n · n.

## b) Recurrencia T(n) = 2T(n−1) + 1

El teorema maestro de bolsillo solo sirve para recurrencias de la forma T(n) = a·T(n/b) + f(n), donde el problema se divide entre b. Aquí el tamaño no se divide, solo se le resta 1 (n−1), por eso el teorema no se puede aplicar.

Esta recurrencia genera dos llamadas más pequeñas por cada llamada, por eso la cantidad se duplica en cada nivel.

| Nivel | Llamadas |
|---|---:|
| 0 | 1 |
| 1 | 2 |
| 2 | 4 |
| ... | ... |
| n | 2^n |

Sumando las llamadas de todos los niveles:

T(n) = 1 + 2 + 4 + ... + 2^n

T(n) = 2^(n+1) − 1

Por lo tanto, su complejidad es **O(2^n)**.

## c) ¿Sirve el voraz por utilidad por Bs?

No siempre. Podemos verlo con el primer caso de las pruebas, donde el presupuesto es de 100 Bs:

| Útil | Costo Bs | Utilidad | Utilidad por Bs |
|---|---:|---:|---:|
| U1 | 20 | 120 | 6 |
| U2 | 40 | 200 | 5 |
| U3 | 60 | 240 | 4 |

El voraz selecciona primero los útiles con mayor utilidad por Bs:

| Paso | Útil | ¿Cabe? | Gastado | Utilidad |
|---|---|---|---:|---:|
| 1 | U1 | Sí | 20 | 120 |
| 2 | U2 | Sí | 60 | 320 |
| 3 | U3 | No | 60 | 320 |

El resultado del voraz es U1 + U2, con una utilidad de 320.

Sin embargo, la mejor combinación es U2 + U3, que utiliza los 100 Bs y consigue una utilidad de 440.

Esto demuestra que elegir primero el útil con mejor relación entre utilidad y costo no siempre da el mejor resultado.

**Estrategia elegida: programación dinámica.**

- `t[i][c]` guarda la mejor utilidad que se puede conseguir usando los primeros i útiles y un presupuesto de c Bs.
- Para cada útil tenemos dos opciones: no comprarlo o comprarlo si alcanza el presupuesto.
- Se comparan ambas opciones y se guarda la que tenga mayor utilidad.
- Lo que se repite es el subproblema (útil i, presupuesto que queda c): en la recursión «lo compro o no lo compro» aparece muchas veces por caminos distintos. La tabla lo calcula una sola vez y lo reutiliza.

**Costo:** O(n · P) en tiempo y memoria, donde n es la cantidad de útiles y P el presupuesto.

## d) Estructura para EstaEnLaCompra

| Estructura | Búsqueda | Costo |
|---|---|---|
| Ingenuo: lista (`Contains` / `in`) | Revisa los elementos uno por uno | O(k) |
| Mejorado: set | Busca mediante una tabla hash | O(1) promedio |

k = cantidad de útiles elegidos.

El set permite encontrar un elemento más rápido porque no necesita recorrer toda la lista para buscarlo.
