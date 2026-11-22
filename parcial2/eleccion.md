# Paul Steffano Velarde chuquimia

# P2.1 · Elegir: turnos de una clínica (variante A)

Código en [`turnos.py`](turnos.py).

## Estructura y costo de cada operación

Elegí combinar dos estructuras: un **min-heap** (`heapq`) de tuplas `(urgencia, llegada, nombre)` para el orden de atención, y un **set** (tabla hash) de nombres para saber quién sigue esperando.

| Operación | Veces por día | Estructura | Costo (mi solución) | Costo (lista simple) |
|---|---:|---|---|---|
| `Registrar(nombre, urgencia)` | 100 000 | heap (`heappush`) + set (`add`) | O(log n) | O(1) |
| `AtenderSiguiente()` | 100 000 | heap (`heappop`) + set (`discard`) | O(log n) | O(n): recorre todo y `pop(i)` corre el resto |
| `EstaEsperando(nombre)` | 30 000 | set (`in`) | O(1) promedio | O(n): búsqueda lineal |
| `Esperando` | (pocas) | `len(set)` | O(1) | O(1) |

**Desempate:** Python compara tuplas elemento por elemento. Por eso `(urgencia, llegada, …)` saca primero la menor urgencia y, si empatan, la menor llegada (el que llegó antes). `llegada` nunca se repite, así que el nombre nunca entra en la comparación.

**Por qué también el set:** un heap solo sabe quién está arriba. Para preguntar por un nombre tendría que recorrerse entero (O(n)). El set responde esa pregunta en O(1) y se mantiene al día: al atender, el nombre sale del heap y del set.

## Por qué no sirve la lista simple (con números, n = 100 000)

Peor caso de un día: llegan los 100 000 y después se los atiende. Uso log₂(100 000) ≈ 17.

| | Lista simple | Heap + set |
|---|---|---|
| Registrar ×100 000 | 100 000 × 1 = **1·10⁵** | 100 000 × 17 = **1,7·10⁶** |
| Atender ×100 000 | se recorren n, n−1, …, 1 ≈ n²/2 = **5·10⁹** | 100 000 × 17 = **1,7·10⁶** |
| EstaEsperando ×30 000 | 30 000 × 100 000 = **3·10⁹** (peor caso) | 30 000 × 1 = **3·10⁴** |
| **Total aproximado** | **≈ 8·10⁹ pasos** | **≈ 3,4·10⁶ pasos** |

La lista simple hace unas **2 300 veces más trabajo**. Medido en Python ([`medicion.md`](medicion.md)), la lista tarda varios segundos con apenas 10 000 pacientes. Con 100 000 serían minutos, y un día real tiene 100 000. La lista solo gana en `Registrar`, que es O(1) contra O(log n). Ese ahorro no compensa nada: atender es lo que domina.

## Cuándo cambiaría de opinión

**Si hubiera muy pocos pacientes** (unas decenas por día), usaría la lista simple: es más fácil de leer y con tan pocos datos la diferencia entre O(n) y O(log n) no se nota.
