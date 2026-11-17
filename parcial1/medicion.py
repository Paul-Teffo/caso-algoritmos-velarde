# Paul Steffano Velarde Chuquimia

import random
import sys
import time



def hay_comprobantes_repetidos_por_pares(comprobantes):
    n = len(comprobantes)
    for a in range(n):
        for b in range(a + 1, n):
            if comprobantes[a] == comprobantes[b]:
                return True
    return False


def hay_comprobantes_repetidos_curado(comprobantes):
    vistos = set()
    for c in comprobantes:
        if c in vistos:
            return True
        vistos.add(c)
    return False


def generar_sin_repetidos(n, semilla=77):
    datos = [1000 + i for i in range(n)]   # 1000, 1001, ..., sin repetidos
    azar = random.Random(semilla)          # semilla fija: siempre la misma mezcla
    azar.shuffle(datos)                    # desordena la lista
    return datos



CASOS = [
    ([1010, 1003, 1009, 1003, 1005], True, "repetido en el medio"),
    ([1010, 1003, 1009, 1004, 1005], False, "sin repetidos"),
    ([], False, "lista vacía"),
    ([1008], False, "un solo elemento"),
    ([1004, 1001, 1002, 1006, 1004], True, "repetido en los extremos"),
]


def correr_casos():
    print("CASOS DE PRUEBA")
    todos_ok = True
    for datos, esperado, que in CASOS:
        copia = list(datos)
        lenta = hay_comprobantes_repetidos_por_pares(datos)
        curada = hay_comprobantes_repetidos_curado(datos)
        intacta = datos == copia          # comprobamos que la cura no tocó la lista
        ok = lenta == esperado and curada == esperado and intacta
        todos_ok = todos_ok and ok
        print(f"{que:<26} esperado {esperado!s:<5} · por pares {lenta!s:<5} · "
              f"mi cura {curada!s:<5} · lista intacta {intacta!s:<5} {'OK' if ok else 'FALLA'}")
    print("Resultado:", "los 5 casos pasan" if todos_ok else "HAY FALLAS")
    print()


def medir(funcion, datos, corridas=3):
    funcion(datos)
    suma = 0.0
    for _ in range(corridas):
        inicio = time.perf_counter()
        funcion(datos)
        suma += time.perf_counter() - inicio
    return suma / corridas * 1000


def correr_medicion(tamanos=(2_000, 4_000, 8_000, 16_000)):
    print("MEDICIÓN EN EL PEOR CASO (lista sin repetidos)")
    print("PROTOCOLO: 1 corrida de calentamiento + 3 corridas medidas + promedio")
    print(f"{'n':>8} {'por pares (ms)':>16} {'x ant.':>8} {'curado (ms)':>13} {'x ant.':>8}")
    ant_lenta = ant_cura = 0.0
    filas = []
    for n in tamanos:
        datos = generar_sin_repetidos(n)
        t_lenta = medir(hay_comprobantes_repetidos_por_pares, datos)
        t_cura = medir(hay_comprobantes_repetidos_curado, datos)
        x_lenta = f"x{t_lenta / ant_lenta:.2f}" if ant_lenta else "—"
        x_cura = f"x{t_cura / ant_cura:.2f}" if ant_cura else "—"
        print(f"{n:>8,} {t_lenta:>16.2f} {x_lenta:>8} {t_cura:>13.4f} {x_cura:>8}")
        filas.append((n, t_lenta, t_cura))
        ant_lenta, ant_cura = t_lenta, t_cura
    print()
    print("Si por pares es O(n²), al duplicar n el tiempo debería subir ~x4.")
    print("Si la cura es O(n), al duplicar n el tiempo debería subir ~x2.")
    return filas


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if modo in ("casos", "todo"):
        correr_casos()
    if modo in ("medir", "todo"):
        correr_medicion()
