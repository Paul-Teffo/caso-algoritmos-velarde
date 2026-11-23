# Paul Velarde
# =============================================================================
# CLASE 10 · HEAPS (MONTÍCULOS), COLAS DE PRIORIDAD Y HEAPSORT  (versión EXPLICADA)
# Port a Python de datos/10-heap.cs. Mismo código que heap.py, con comentarios.
#
# Un heap es un árbol binario COMPLETO guardado en un arreglo (una lista), con
# una regla: cada padre es menor o igual que sus hijos (heap mínimo).
#   - El menor siempre está en la posición 0.
#   - Hijos de i: 2i+1 y 2i+2.   Padre de i: (i-1)//2.
# Partes A, B y C: trazas y conteos exactos (A y B salen iguales al C#).
# Partes D y E: tiempos con protocolo (calentar, 3 corridas, promedio).
#
# Uso:  python heap_explicado.py [todo|heap|prioridad|ordenar|torneo|topk]
# =============================================================================

import heapq    # el heap mínimo que trae Python (equivale a PriorityQueue de .NET)
import math     # log2 para comparar con n log n
import random   # datos al azar con semilla fija (reproducibles)
import sys      # elegir la parte desde la línea de comandos
import time     # perf_counter para medir


# -----------------------------------------------------------------------------
# EL HEAP MÍNIMO, ESCRITO A MANO
# En C# usaba un arreglo fijo de 64 + un contador _n. En Python una lista ya
# crece sola: append agrega al final y pop() saca el último, ambos O(1).
# -----------------------------------------------------------------------------
class HeapMin:
    def __init__(self):
        self._a = []

    @property
    def cantidad(self):
        return len(self._a)

    @property
    def minimo(self):
        return self._a[0]          # el menor siempre en la raíz: O(1)

    def insertar(self, x, traza=False):
        """Agrega al final y lo SUBE mientras sea menor que su padre. O(log n)."""
        a = self._a
        a.append(x)                # 1) va a la primera hoja libre
        i = len(a) - 1
        while i > 0:               # 2) sube como mucho la altura del árbol (log n)
            padre = (i - 1) // 2   # // es división entera (en C# / con int ya lo es)
            if a[padre] <= a[i]:   # la regla del heap ya se cumple: parar
                break
            if traza:
                print(f"      {a[i]} es menor que su padre {a[padre]} → intercambian (sube)")
            a[padre], a[i] = a[i], a[padre]   # intercambio en una línea
            i = padre

    def extraer_minimo(self, traza=False):
        """Saca la raíz, pone el último arriba y lo BAJA. O(log n)."""
        a = self._a
        minimo = a[0]
        ultimo = a.pop()           # sacar el último es O(1)...
        if a:                      # (si quedó vacío no hay nada que reacomodar)
            a[0] = ultimo          # ...y pasa a la raíz
        n = len(a)
        i = 0
        while True:                # baja hasta que sus hijos sean mayores
            izq, der, menor = 2 * i + 1, 2 * i + 2, i
            if izq < n and a[izq] < a[menor]:
                menor = izq
            if der < n and a[der] < a[menor]:
                menor = der
            if menor == i:         # ya es menor que sus dos hijos: parar
                break
            if traza:
                print(f"      {a[i]} es mayor que su hijo {a[menor]} → intercambian (baja)")
            a[i], a[menor] = a[menor], a[i]
            i = menor
        return minimo

    def contenido(self):
        return "[" + ", ".join(map(str, self._a)) + "]"


# -----------------------------------------------------------------------------
# PARTE A · INSERTAR Y EXTRAER, PASO A PASO (traza exacta, igual al C#)
# -----------------------------------------------------------------------------
def parte_a():
    print("PARTE A · UN HEAP MÍNIMO CON 7 CLAVES (el arreglo ES el árbol)")
    heap = HeapMin()
    for x in [50, 30, 70, 20, 40, 60, 10]:
        print(f"  Insertar {x:2}:")    # {x:2} = ancho 2, como {x,2} en C#
        heap.insertar(x, traza=True)
        print(f"    arreglo: {heap.contenido()}   menor = {heap.minimo}")
    print()
    print("  Extraer el menor, tres veces (siempre sale el de la posición 0):")
    for _ in range(3):
        salio = heap.extraer_minimo(traza=True)
        print(f"    sale {salio:2}   → arreglo: {heap.contenido()}")
    print()
    print("  Ver el menor cuesta O(1). Insertar y extraer cuestan O(log n): "
          "se sube o se baja a lo sumo la altura del árbol.")


# -----------------------------------------------------------------------------
# PARTE B · COLA DE PRIORIDAD: LA FILA DEL HOSPITAL
# PriorityQueue<string,(gravedad,llegada)> de C#  ->  heapq con tuplas
# (gravedad, llegada, nombre). Python compara tuplas elemento por elemento:
# primero gravedad y, si empatan, llegada => desempate "el que llegó antes".
# Es el mismo patrón que usamos en parcial2/turnos.py.
# -----------------------------------------------------------------------------
def parte_b():
    print("PARTE B · LA FILA DEL HOSPITAL: primero el más grave, no el que llegó primero")
    llegadas = [("Ana", 4), ("Beto", 2), ("Carla", 5), ("Diego", 1), ("Elena", 3), ("Fabian", 2)]
    print("  (gravedad 1 = crítico ... 5 = leve; en un empate, el que llegó antes)")
    print()
    print("  Llegan en este orden: " + ", ".join(f"{n}({g})" for n, g in llegadas))
    cola = []
    for i, (nombre, gravedad) in enumerate(llegadas):    # i = orden de llegada
        heapq.heappush(cola, (gravedad, i, nombre))      # O(log n)
    atendidos = []
    while cola:
        gravedad, _, nombre = heapq.heappop(cola)        # O(log n): sale el más grave
        atendidos.append(f"{nombre}({gravedad})")
    print("  Los atienden en este orden: " + ", ".join(atendidos))
    print()
    print("  Con una cola normal (FIFO) Diego, que es el crítico, habría esperado a los otros cinco.")
    print("  heapq de Python es un heap: heappush y heappop cuestan O(log n); ver el primero (cola[0]), O(1).")


# -----------------------------------------------------------------------------
# PARTE C · HEAPSORT, CONTANDO COMPARACIONES
# Usa un heap MÁXIMO dentro del mismo arreglo (ordena "en el lugar").
# C# pasaba el contador con 'ref long c'; Python no tiene ref para números,
# así que uso una lista de un elemento [0] que sí se modifica desde adentro.
# -----------------------------------------------------------------------------
def hundir(a, i, n, contador):
    """Baja a[i] hasta que sea mayor que sus hijos (heap máximo), contando comparaciones."""
    while True:
        izq = 2 * i + 1
        der = izq + 1
        mayor = i
        if izq < n:
            contador[0] += 1
            if a[izq] > a[mayor]:
                mayor = izq
        if der < n:
            contador[0] += 1
            if a[der] > a[mayor]:
                mayor = der
        if mayor == i:
            return
        a[i], a[mayor] = a[mayor], a[i]
        i = mayor


def heap_sort(a):
    contador = [0]
    n = len(a)
    # 1) armar el heap máximo desde la mitad hacia atrás: O(n)
    for i in range(n // 2 - 1, -1, -1):
        hundir(a, i, n, contador)
    # 2) n veces: el mayor (raíz) va al final y se rearma el resto: O(n log n)
    for fin in range(n - 1, 0, -1):
        a[0], a[fin] = a[fin], a[0]
        hundir(a, 0, fin, contador)
    return contador[0]


def esta_ordenado(a):
    return all(a[i - 1] <= a[i] for i in range(1, len(a)))


def parte_c():
    print("PARTE C · HEAPSORT: armar un heap y sacar el mayor n veces")
    print(f"  {'n':>8} {'comparaciones':>15} {'x':>6} {'n × log2 n':>14} {'comparaciones / (n log2 n)':>28}")
    # Semilla 21 como en C#. OJO: el generador de Python no es el de .NET, así
    # que los datos (y los conteos exactos) difieren un poco; las razones no.
    azar = random.Random(21)
    anterior = 0
    for n in [1_000, 2_000, 4_000, 8_000, 16_000]:
        datos = [azar.randrange(2**31 - 1) for _ in range(n)]   # como azar.Next()
        c = heap_sort(datos)
        if not esta_ordenado(datos):          # verificar antes de confiar en el conteo
            raise RuntimeError("HeapSort dejó el arreglo desordenado")
        nlogn = n * math.log2(n)
        razon = "—" if anterior == 0 else f"x{c / anterior:.1f}"
        print(f"  {n:>8,} {c:>15,} {razon:>6} {nlogn:>14,.0f} {c / nlogn:>28.2f}")
        anterior = c
    print("  Doble de datos: un poco más del doble de comparaciones (n log n). "
          "Hasta 2 comparaciones por nivel: aquí ~1,7 a 1,8 × n log2 n.")
    print("  Garantía: n log n SIEMPRE (no hay peor caso malo como en QuickSort) "
          "y ordena en el lugar, sin memoria extra.")


# -----------------------------------------------------------------------------
# PARTE D · EL TORNEO FINAL (se suma HeapSort)
# -----------------------------------------------------------------------------
def merge_sort(a):
    tmp = [0] * len(a)                # memoria extra O(n)
    _mezclar(a, tmp, 0, len(a) - 1)


def _mezclar(a, tmp, ini, fin):
    if ini >= fin:
        return
    medio = ini + (fin - ini) // 2
    _mezclar(a, tmp, ini, medio)      # ordenar mitad izquierda
    _mezclar(a, tmp, medio + 1, fin)  # ordenar mitad derecha
    i, j, k = ini, medio + 1, ini     # mezclar las dos mitades en tmp
    while i <= medio and j <= fin:
        if a[i] <= a[j]:              # <= mantiene el orden de iguales (estable)
            tmp[k] = a[i]
            i += 1
        else:
            tmp[k] = a[j]
            j += 1
        k += 1
    while i <= medio:
        tmp[k] = a[i]
        i += 1
        k += 1
    while j <= fin:
        tmp[k] = a[j]
        j += 1
        k += 1
    a[ini:fin + 1] = tmp[ini:fin + 1] # copiar de vuelta (slice = el for del C#)


def quick_sort(a, ini=0, fin=None):
    if fin is None:                   # permite llamarlo como quick_sort(lista)
        fin = len(a) - 1
    if ini >= fin:
        return
    p = ini + (fin - ini) // 2        # pivote del medio (evita el peor caso con datos ordenados)
    a[p], a[fin] = a[fin], a[p]
    pivote = a[fin]
    i = ini
    for j in range(ini, fin):         # partición de Lomuto
        if a[j] < pivote:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[fin] = a[fin], a[i]
    quick_sort(a, ini, i - 1)
    quick_sort(a, i + 1, fin)


def promedio(accion, corridas=3):
    """PROTOCOLO: 1 calentamiento + 3 corridas medidas + promedio (en ms)."""
    accion()
    suma = 0.0
    for _ in range(corridas):
        inicio = time.perf_counter()
        accion()
        suma += time.perf_counter() - inicio
    return suma / corridas * 1000


def promedio_con_copia(original, ordenar, corridas=3):
    """Igual que promedio(), pero cada corrida ordena una COPIA desordenada
    (si no, desde la 2ª corrida ordenaría datos ya ordenados)."""
    trabajo = original[:]
    ordenar(trabajo)                  # calentamiento + verificación
    if not esta_ordenado(trabajo):
        raise RuntimeError("quedó desordenado")
    suma = 0.0
    for _ in range(corridas):
        trabajo = original[:]         # la copia NO entra en el tiempo
        inicio = time.perf_counter()
        ordenar(trabajo)
        suma += time.perf_counter() - inicio
    return suma / corridas * 1000


def parte_d():
    print("PARTE D · EL TORNEO FINAL DE ORDENAMIENTOS (datos al azar)")
    print(f"  {'n':>10} {'HeapSort ms':>13} {'MergeSort ms':>14} {'QuickSort ms':>14} {'list.sort ms':>14}")
    # Tamaños más chicos que en C# (100k, 1M, 4M): en Python puro 4 millones
    # tardaría minutos por algoritmo. La forma (n log n) se ve igual.
    for n in [10_000, 100_000, 200_000]:
        azar = random.Random(8)
        original = [azar.randrange(2**31 - 1) for _ in range(n)]
        h = promedio_con_copia(original, heap_sort)
        m = promedio_con_copia(original, merge_sort)
        q = promedio_con_copia(original, quick_sort)
        s = promedio_con_copia(original, list.sort)   # equivale a Array.Sort
        print(f"  {n:>10,} {h:>13.1f} {m:>14.1f} {q:>14.1f} {s:>14.1f}")
    print("  Los cuatro son n log n. HeapSort suele quedar más lento que QuickSort: "
          "salta por la memoria (padre e hijos están lejos).")
    print("  list.sort (Timsort, escrito en C) le gana por mucho a los tres escritos en Python puro.")


# -----------------------------------------------------------------------------
# PARTE E · EL USO REAL: LOS k MAYORES SIN ORDENAR TODO
# Heap MÍNIMO de tamaño k: en la raíz queda el MENOR de los k mejores. Si llega
# uno mayor que ese, reemplaza la raíz. Cada dato cuesta O(log k) => O(n log k).
# -----------------------------------------------------------------------------
def parte_e():
    n, k = 1_000_000, 10              # C# usaba 5.000.000; en Python bajo a 1.000.000
    print(f"PARTE E · LOS {k} MEJORES PUNTAJES DE {n:,} (ranking)".replace(",", "."))
    azar = random.Random(4)
    puntajes = [azar.randrange(2**31 - 1) for _ in range(n)]
    resultado = {}                    # para comparar lo que devuelve cada método

    def con_heap():
        heap = []
        for p in puntajes:
            if len(heap) < k:
                heapq.heappush(heap, p)
            elif p > heap[0]:              # heap[0] = Peek(): O(1)
                heapq.heapreplace(heap, p) # = Dequeue + Enqueue en un paso, O(log k)
        resultado["heap"] = sorted(heap, reverse=True)
        # (Python ya trae esto hecho: heapq.nlargest(k, puntajes))

    def con_sort():
        copia = sorted(puntajes)          # ordenar TODO: O(n log n)
        resultado["sort"] = copia[-k:][::-1]

    th = promedio(con_heap)
    ts = promedio(con_sort)
    print(f"  Heap de tamaño {k}  : O(n log k)   {th:8.1f} ms")
    print(f"  Ordenar todo      : O(n log n)   {ts:8.1f} ms")
    print(f"  ¿Mismos {k} mayores? {'sí' if resultado['heap'] == resultado['sort'] else 'NO'}")
    print("  El heap solo mantiene 10 elementos: cada dato nuevo cuesta a lo sumo log 10. "
          "Es el truco de los rankings.")


# Nombre de la parte -> función (como los argumentos del 'dotnet run -- ...')
PARTES = {"heap": parte_a, "prioridad": parte_b, "ordenar": parte_c, "torneo": parte_d, "topk": parte_e}


def main():
    elegida = sys.argv[1] if len(sys.argv) > 1 else "todo"
    partes = list(PARTES.values()) if elegida == "todo" else [PARTES[elegida]]
    for i, parte in enumerate(partes):
        if i > 0:                     # separador entre partes, como en el C#
            print()
            print("=" * 100)
        parte()


if __name__ == "__main__":
    main()
