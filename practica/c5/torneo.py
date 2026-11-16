

import csv
import random
import sys
import time
from pathlib import Path

TAMANOS = [10_000, 20_000, 40_000, 80_000]
CORRIDAS = 3
SEMILLA = 2026
CARPETA = Path(__file__).resolve().parent


# ---------------------------------------------------------------- algoritmos

def insercion(a):
    """Ordenamiento por insercion, in-place. O(n^2)."""
    for i in range(1, len(a)):
        x = a[i]
        j = i - 1
        while j >= 0 and a[j] > x:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = x
    return a


def merge_sort(a):
   
    aux = a[:]

    def ordenar(lo, hi):  # ordena a[lo:hi]
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        ordenar(lo, mid)
        ordenar(mid, hi)
        if a[mid - 1] <= a[mid]:  # ya estan en orden
            return
        aux[lo:hi] = a[lo:hi]
        i, j, k = lo, mid, lo
        while i < mid and j < hi:
            if aux[i] <= aux[j]:
                a[k] = aux[i]
                i += 1
            else:
                a[k] = aux[j]
                j += 1
            k += 1
        while i < mid:
            a[k] = aux[i]
            i += 1
            k += 1
       

    ordenar(0, len(a))
    return a


def quick_sort(a):
   
    rnd = random.Random(0)

    def ordenar(lo, hi):  
        while lo < hi:
            p = a[rnd.randint(lo, hi)]
            i, j = lo, hi
            while i <= j:
                while a[i] < p:
                    i += 1
                while a[j] > p:
                    j -= 1
                if i <= j:
                    a[i], a[j] = a[j], a[i]
                    i += 1
                    j -= 1
            if j - lo < hi - i:
                ordenar(lo, j)
                lo = i
            else:
                ordenar(i, hi)
                hi = j

    ordenar(0, len(a) - 1)
    return a


def sort_python(a):
    """sort() nativo de Python (Timsort en C)."""
    a.sort()
    return a


COMPETIDORES = [
    ("Insercion", "O(n^2)", insercion),
    ("MergeSort", "O(n log n)", merge_sort),
    ("QuickSort", "O(n log n)", quick_sort),
    ("sort() Python", "O(n log n)", sort_python),
]




def esta_ordenado(a):
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def generar(n):
    rnd = random.Random(SEMILLA + n)
    return [rnd.randint(0, 1_000_000) for _ in range(n)]


def medir(func, datos):
    copia = datos[:]  # la copia no se cuenta en el tiempo
    t0 = time.perf_counter()
    func(copia)
    t = time.perf_counter() - t0
    return t, copia


# ---------------------------------------------------------------- torneo

def main():
    tamanos = [int(x) for x in sys.argv[1:]] or TAMANOS
    filas = []

    # 0) Verificacion de correccion antes de medir
    print("Verificando que cada competidor ordene correctamente...")
    casos = [[], [1], [2, 1], [3, 3, 1, 2, 3], list(range(50, 0, -1)), generar(2_000)]
    for nombre, _, func in COMPETIDORES:
        for caso in casos:
            res = func(caso[:])
            if res != sorted(caso):
                sys.exit(f"ERROR: {nombre} no ordena bien el caso {caso[:10]}...")
        print(f"  OK  {nombre}")
    print()

    for n in tamanos:
        datos = generar(n)
        esperado = sorted(datos)
        print(f"n = {n:,}".replace(",", "."))
        for nombre, orden, func in COMPETIDORES:
            # 1) calentamiento (no se cuenta) + verificacion sobre el arreglo real
            _, salida = medir(func, datos)
            if salida != esperado or not esta_ordenado(salida):
                sys.exit(f"ERROR: {nombre} no dejo ordenado el arreglo de n={n}")

            # 2) 3 corridas medidas
            tiempos = []
            for _ in range(CORRIDAS):
                t, salida = medir(func, datos)
                assert salida == esperado
                tiempos.append(t)
            prom = sum(tiempos) / CORRIDAS

            filas.append({
                "algoritmo": nombre, "orden": orden, "n": n,
                "corrida1_s": tiempos[0], "corrida2_s": tiempos[1],
                "corrida3_s": tiempos[2], "promedio_s": prom,
            })
            print(f"  {nombre:<14} {prom * 1000:>12.2f} ms   "
                  f"({', '.join(f'{t * 1000:.1f}' for t in tiempos)})")
        print()

    guardar(filas, tamanos)


def guardar(filas, tamanos):
    with open(CARPETA / "resultados.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        for fila in filas:
            w.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in fila.items()})

    prom = {(f["algoritmo"], f["n"]): f["promedio_s"] for f in filas}
    fmt_n = lambda n: f"{n:,}".replace(",", ".")

    lineas = [
        "# Resultados del torneo (promedio de 3 corridas, en milisegundos)",
        "",
        f"Python {sys.version.split()[0]} · {CORRIDAS} corridas + 1 de calentamiento · "
        f"enteros aleatorios (semilla {SEMILLA})",
        "",
        "| Algoritmo | Orden | " + " | ".join(f"n = {fmt_n(n)}" for n in tamanos) + " |",
        "|---|---|" + "---:|" * len(tamanos),
    ]
    for nombre, orden, _ in COMPETIDORES:
        celdas = " | ".join(f"{prom[(nombre, n)] * 1000:,.2f}" for n in tamanos)
        lineas.append(f"| {nombre} | {orden} | {celdas} |")

    # razon de crecimiento al duplicar n
    if len(tamanos) > 1:
        lineas += [
            "",
            "## Cuanto crece el tiempo al duplicar n (t(2n) / t(n))",
            "",
            "Teorico: O(n^2) -> x4 · O(n log n) -> un poco mas de x2",
            "",
            "| Algoritmo | " + " | ".join(
                f"{fmt_n(a)}→{fmt_n(b)}" for a, b in zip(tamanos, tamanos[1:])) + " |",
            "|---|" + "---:|" * (len(tamanos) - 1),
        ]
        for nombre, _, _ in COMPETIDORES:
            razones = " | ".join(
                f"x{prom[(nombre, b)] / prom[(nombre, a)]:.2f}"
                for a, b in zip(tamanos, tamanos[1:]))
            lineas.append(f"| {nombre} | {razones} |")

    (CARPETA / "resultados.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("Guardado: resultados.csv y resultados.md")


if __name__ == "__main__":
    main()
