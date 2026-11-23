# Paul Velarde
import heapq
import math
import random
import sys
import time


class HeapMin:
    def __init__(self):
        self._a = []

    @property
    def cantidad(self):
        return len(self._a)

    @property
    def minimo(self):
        return self._a[0]

    def insertar(self, x, traza=False):
        a = self._a
        a.append(x)
        i = len(a) - 1
        while i > 0:
            padre = (i - 1) // 2
            if a[padre] <= a[i]:
                break
            if traza:
                print(f"      {a[i]} es menor que su padre {a[padre]} → intercambian (sube)")
            a[padre], a[i] = a[i], a[padre]
            i = padre

    def extraer_minimo(self, traza=False):
        a = self._a
        minimo = a[0]
        ultimo = a.pop()
        if a:
            a[0] = ultimo
        n = len(a)
        i = 0
        while True:
            izq, der, menor = 2 * i + 1, 2 * i + 2, i
            if izq < n and a[izq] < a[menor]:
                menor = izq
            if der < n and a[der] < a[menor]:
                menor = der
            if menor == i:
                break
            if traza:
                print(f"      {a[i]} es mayor que su hijo {a[menor]} → intercambian (baja)")
            a[i], a[menor] = a[menor], a[i]
            i = menor
        return minimo

    def contenido(self):
        return "[" + ", ".join(map(str, self._a)) + "]"


def parte_a():
    print("PARTE A · UN HEAP MÍNIMO CON 7 CLAVES (el arreglo ES el árbol)")
    heap = HeapMin()
    for x in [50, 30, 70, 20, 40, 60, 10]:
        print(f"  Insertar {x:2}:")
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


def parte_b():
    print("PARTE B · LA FILA DEL HOSPITAL: primero el más grave, no el que llegó primero")
    llegadas = [("Ana", 4), ("Beto", 2), ("Carla", 5), ("Diego", 1), ("Elena", 3), ("Fabian", 2)]
    print("  (gravedad 1 = crítico ... 5 = leve; en un empate, el que llegó antes)")
    print()
    print("  Llegan en este orden: " + ", ".join(f"{n}({g})" for n, g in llegadas))
    cola = []
    for i, (nombre, gravedad) in enumerate(llegadas):
        heapq.heappush(cola, (gravedad, i, nombre))
    atendidos = []
    while cola:
        gravedad, _, nombre = heapq.heappop(cola)
        atendidos.append(f"{nombre}({gravedad})")
    print("  Los atienden en este orden: " + ", ".join(atendidos))
    print()
    print("  Con una cola normal (FIFO) Diego, que es el crítico, habría esperado a los otros cinco.")
    print("  heapq de Python es un heap: heappush y heappop cuestan O(log n); ver el primero (cola[0]), O(1).")


def hundir(a, i, n, contador):
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
    for i in range(n // 2 - 1, -1, -1):
        hundir(a, i, n, contador)
    for fin in range(n - 1, 0, -1):
        a[0], a[fin] = a[fin], a[0]
        hundir(a, 0, fin, contador)
    return contador[0]


def esta_ordenado(a):
    return all(a[i - 1] <= a[i] for i in range(1, len(a)))


def parte_c():
    print("PARTE C · HEAPSORT: armar un heap y sacar el mayor n veces")
    print(f"  {'n':>8} {'comparaciones':>15} {'x':>6} {'n × log2 n':>14} {'comparaciones / (n log2 n)':>28}")
    azar = random.Random(21)
    anterior = 0
    for n in [1_000, 2_000, 4_000, 8_000, 16_000]:
        datos = [azar.randrange(2**31 - 1) for _ in range(n)]
        c = heap_sort(datos)
        if not esta_ordenado(datos):
            raise RuntimeError("HeapSort dejó el arreglo desordenado")
        nlogn = n * math.log2(n)
        razon = "—" if anterior == 0 else f"x{c / anterior:.1f}"
        print(f"  {n:>8,} {c:>15,} {razon:>6} {nlogn:>14,.0f} {c / nlogn:>28.2f}")
        anterior = c
    print("  Doble de datos: un poco más del doble de comparaciones (n log n). "
          "Hasta 2 comparaciones por nivel: aquí ~1,7 a 1,8 × n log2 n.")
    print("  Garantía: n log n SIEMPRE (no hay peor caso malo como en QuickSort) "
          "y ordena en el lugar, sin memoria extra.")


def merge_sort(a):
    tmp = [0] * len(a)
    _mezclar(a, tmp, 0, len(a) - 1)


def _mezclar(a, tmp, ini, fin):
    if ini >= fin:
        return
    medio = ini + (fin - ini) // 2
    _mezclar(a, tmp, ini, medio)
    _mezclar(a, tmp, medio + 1, fin)
    i, j, k = ini, medio + 1, ini
    while i <= medio and j <= fin:
        if a[i] <= a[j]:
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
    a[ini:fin + 1] = tmp[ini:fin + 1]


def quick_sort(a, ini=0, fin=None):
    if fin is None:
        fin = len(a) - 1
    if ini >= fin:
        return
    p = ini + (fin - ini) // 2
    a[p], a[fin] = a[fin], a[p]
    pivote = a[fin]
    i = ini
    for j in range(ini, fin):
        if a[j] < pivote:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[fin] = a[fin], a[i]
    quick_sort(a, ini, i - 1)
    quick_sort(a, i + 1, fin)


def promedio(accion, corridas=3):
    accion()
    suma = 0.0
    for _ in range(corridas):
        inicio = time.perf_counter()
        accion()
        suma += time.perf_counter() - inicio
    return suma / corridas * 1000


def promedio_con_copia(original, ordenar, corridas=3):
    trabajo = original[:]
    ordenar(trabajo)
    if not esta_ordenado(trabajo):
        raise RuntimeError("quedó desordenado")
    suma = 0.0
    for _ in range(corridas):
        trabajo = original[:]
        inicio = time.perf_counter()
        ordenar(trabajo)
        suma += time.perf_counter() - inicio
    return suma / corridas * 1000


def parte_d():
    print("PARTE D · EL TORNEO FINAL DE ORDENAMIENTOS (datos al azar)")
    print(f"  {'n':>10} {'HeapSort ms':>13} {'MergeSort ms':>14} {'QuickSort ms':>14} {'list.sort ms':>14}")
    for n in [10_000, 100_000, 200_000]:
        azar = random.Random(8)
        original = [azar.randrange(2**31 - 1) for _ in range(n)]
        h = promedio_con_copia(original, heap_sort)
        m = promedio_con_copia(original, merge_sort)
        q = promedio_con_copia(original, quick_sort)
        s = promedio_con_copia(original, list.sort)
        print(f"  {n:>10,} {h:>13.1f} {m:>14.1f} {q:>14.1f} {s:>14.1f}")
    print("  Los cuatro son n log n. HeapSort suele quedar más lento que QuickSort: "
          "salta por la memoria (padre e hijos están lejos).")
    print("  list.sort (Timsort, escrito en C) le gana por mucho a los tres escritos en Python puro.")


def parte_e():
    n, k = 1_000_000, 10
    print(f"PARTE E · LOS {k} MEJORES PUNTAJES DE {n:,} (ranking)".replace(",", "."))
    azar = random.Random(4)
    puntajes = [azar.randrange(2**31 - 1) for _ in range(n)]
    resultado = {}

    def con_heap():
        heap = []
        for p in puntajes:
            if len(heap) < k:
                heapq.heappush(heap, p)
            elif p > heap[0]:
                heapq.heapreplace(heap, p)
        resultado["heap"] = sorted(heap, reverse=True)

    def con_sort():
        copia = sorted(puntajes)
        resultado["sort"] = copia[-k:][::-1]

    th = promedio(con_heap)
    ts = promedio(con_sort)
    print(f"  Heap de tamaño {k}  : O(n log k)   {th:8.1f} ms")
    print(f"  Ordenar todo      : O(n log n)   {ts:8.1f} ms")
    print(f"  ¿Mismos {k} mayores? {'sí' if resultado['heap'] == resultado['sort'] else 'NO'}")
    print("  El heap solo mantiene 10 elementos: cada dato nuevo cuesta a lo sumo log 10. "
          "Es el truco de los rankings.")


PARTES = {"heap": parte_a, "prioridad": parte_b, "ordenar": parte_c, "torneo": parte_d, "topk": parte_e}


def main():
    elegida = sys.argv[1] if len(sys.argv) > 1 else "todo"
    partes = list(PARTES.values()) if elegida == "todo" else [PARTES[elegida]]
    for i, parte in enumerate(partes):
        if i > 0:
            print()
            print("=" * 100)
        parte()


if __name__ == "__main__":
    main()
