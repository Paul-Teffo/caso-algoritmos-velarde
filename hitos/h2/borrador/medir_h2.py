# Paul Steffano Velarde Chuquimia
# H2: ingenua vs adecuada para las operaciones que más hace el simulador.
#
#   A. Armar examen  -> rango por clave (materia) + k al azar   -> SortedList (árbol)
#   B. Corregir      -> solo buscar por clave (id de pregunta) -> dict (hash)
#   C. Puesto/nota   -> orden + rango (cuántas notas superan)   -> SortedList (árbol)
#
# Uso:  python medir_h2.py                 (tamaños completos)
#       python medir_h2.py 2877 10000      (prueba rápida con tamaños propios)
# Requiere: pip install sortedcontainers

import bisect
import random
import sys
import time

from sortedcontainers import SortedList

SEMILLA = 2026
K = 100                       # preguntas por examen (máximo real pedido)
MATERIAS = {                  # proporciones reales del banco (H1)
    1: ("Medicina Interna", 1096),
    2: ("Ginecoobstetricia", 664),
    3: ("Cirugía", 625),
    4: ("Pediatría", 346),
    5: ("Salud Pública", 146),
}
ELEGIDAS = (4, 5)             # el estudiante elige Pediatría + Salud Pública
TAMANOS = (2_877, 10_000, 50_000, 100_000, 500_000)
EXAMENES_POR_CORRIDA = 20     # operaciones repetidas dentro de cada corrida
NOTAS_POR_CORRIDA = 200


# ---------- datos: banco sintético con la misma distribución real ----------

def generar_banco(n, semilla=SEMILLA):
    azar = random.Random(semilla)
    ids_materia = list(MATERIAS)
    pesos = [MATERIAS[m][1] for m in ids_materia]
    banco = []
    for pid in range(1, n + 1):
        materia = azar.choices(ids_materia, weights=pesos)[0]
        banco.append((pid, materia, azar.choice("ABCDE")))   # (id, materia_id, correcta)
    return banco


def generar_respuestas(banco, k, semilla=SEMILLA):
    azar = random.Random(semilla + 1)
    return [(p[0], azar.choice("ABCDE")) for p in azar.sample(banco, k)]


# ---------- A. armar examen ----------

def armar_ingenua(banco, elegidas, k, azar):
    """Copia de ORDER BY RAND(): filtra todo el banco, da una clave al azar a cada fila y ordena. O(n log n)."""
    candidatas = [p for p in banco if p[1] in elegidas]                     # O(n)
    candidatas.sort(key=lambda _: azar.random())                           # O(n log n)
    return [p[0] for p in candidatas[:k]]


def indexar_por_materia(banco):
    """Árbol ordenado por (materia_id, id). Se arma una vez; agregar pregunta = add() O(log n)."""
    return SortedList((p[1], p[0]) for p in banco)


def armar_adecuada(arbol, elegidas, k, azar):
    """Rango por materia con bisect O(log n) y k accesos por posición O(log n). Total O(m log n + k log n)."""
    rangos = []
    for m in elegidas:
        ini = arbol.bisect_left((m, 0))
        fin = arbol.bisect_left((m + 1, 0))
        rangos.append((ini, fin))
    total = sum(fin - ini for ini, fin in rangos)
    elegidos = azar.sample(range(total), min(k, total))                    # O(k), sin mirar las n filas
    ids = []
    for r in elegidos:
        for ini, fin in rangos:
            if r < fin - ini:
                ids.append(arbol[ini + r][1])                              # acceso por posición O(log n)
                break
            r -= fin - ini
    return ids


# ---------- B. corregir ----------

def corregir_ingenua(banco, respuestas):
    """Por cada respuesta recorre el banco buscando la pregunta (como una consulta por respuesta). O(k·n)."""
    nota = 0
    for pid, marcada in respuestas:
        for p in banco:
            if p[0] == pid:
                nota += p[2] == marcada
                break
    return nota


def corregir_arbol(arbol_ids, respuestas):
    """SortedList de (id, correcta) + bisect: O(k log n). Sirve, pero aquí no se usa el orden.
    (No se usa SortedDict porque hereda de dict: su búsqueda por clave es un hash, no el árbol.)"""
    nota = 0
    for pid, marcada in respuestas:
        nota += arbol_ids[arbol_ids.bisect_left((pid,))][1] == marcada
    return nota


def corregir_adecuada(tabla, respuestas):
    """dict (hash): O(k), cada búsqueda O(1). Solo se busca por clave, no hace falta orden."""
    return sum(tabla[pid] == marcada for pid, marcada in respuestas)


# ---------- C. puesto de una nota entre todos los simulacros ----------

def puesto_ingenua(notas, nota):
    """Lista desordenada: agrega y cuenta cuántas notas la superan recorriendo todo. O(n)."""
    notas.append(nota)
    return 1 + sum(1 for x in notas if x > nota)


def puesto_adecuada(arbol_notas, nota):
    """SortedList: add O(log n) + bisect O(log n) para saber cuántas la superan."""
    arbol_notas.add(nota)
    return 1 + len(arbol_notas) - arbol_notas.bisect_right(nota)


# ---------- verificación ----------

def verificar(banco):
    elegidas = set(ELEGIDAS)
    pertenece = {p[0]: p[1] for p in banco}
    arbol = indexar_por_materia(banco)
    for armar, estructura in ((armar_ingenua, banco), (armar_adecuada, arbol)):
        ids = armar(estructura, elegidas, K, random.Random(1))
        assert len(ids) == K, f"{armar.__name__}: no devuelve k preguntas"
        assert len(set(ids)) == K, f"{armar.__name__}: preguntas repetidas"
        assert all(pertenece[i] in elegidas for i in ids), f"{armar.__name__}: materia equivocada"
    # caso borde: pedir más preguntas de las que hay
    pocas = [p for p in banco if p[1] == 5][:3] + [p for p in banco if p[1] == 1][:10]
    assert len(armar_adecuada(indexar_por_materia(pocas), {5}, K, random.Random(1))) == 3

    respuestas = generar_respuestas(banco, K)
    tabla = {p[0]: p[2] for p in banco}
    a = corregir_ingenua(banco, respuestas)
    b = corregir_arbol(SortedList(tabla.items()), respuestas)
    c = corregir_adecuada(tabla, respuestas)
    assert a == b == c, f"corrección distinta: {a} {b} {c}"

    azar = random.Random(3)
    notas, arbol_notas = [], SortedList()
    for _ in range(300):
        nota = azar.randint(0, 100)
        assert puesto_ingenua(notas, nota) == puesto_adecuada(arbol_notas, nota)
    print("Verificación: armar, corregir y puesto dan resultados correctos e iguales.\n")


# ---------- medición ----------

def medir(trabajo, repeticiones, corridas=3):
    """1 calentamiento + 3 corridas medidas; devuelve ms promedio por operación."""
    trabajo()
    suma = 0.0
    for _ in range(corridas):
        inicio = time.perf_counter()
        trabajo()
        suma += time.perf_counter() - inicio
    return suma / corridas / repeticiones * 1000


def correr(tamanos):
    elegidas = set(ELEGIDAS)
    filas = []
    print(f"Examen de k = {K} preguntas de {' + '.join(MATERIAS[m][0] for m in ELEGIDAS)}")
    print("Protocolo: 1 calentamiento + 3 corridas medidas, tiempo promedio por operación (ms)\n")
    print(f"{'n':>9} | {'armar ing.':>11} {'armar árbol':>12} | {'corr. ing.':>11} "
          f"{'corr. árbol':>12} {'corr. dict':>11} | {'puesto ing.':>12} {'puesto árbol':>13}")
    for n in tamanos:
        banco = generar_banco(n)
        arbol = indexar_por_materia(banco)
        tabla = {p[0]: p[2] for p in banco}
        arbol_ids = SortedList(tabla.items())
        respuestas = generar_respuestas(banco, K)
        azar = random.Random(SEMILLA)
        notas_base = [azar.randint(0, 100) for _ in range(n)]
        nuevas = [azar.randint(0, 100) for _ in range(NOTAS_POR_CORRIDA)]

        t = {}
        t["armar_ing"] = medir(lambda: [armar_ingenua(banco, elegidas, K, azar)
                                        for _ in range(EXAMENES_POR_CORRIDA)], EXAMENES_POR_CORRIDA)
        t["armar_arbol"] = medir(lambda: [armar_adecuada(arbol, elegidas, K, azar)
                                          for _ in range(EXAMENES_POR_CORRIDA)], EXAMENES_POR_CORRIDA)
        t["corr_ing"] = medir(lambda: corregir_ingenua(banco, respuestas), 1)
        t["corr_arbol"] = medir(lambda: [corregir_arbol(arbol_ids, respuestas)
                                         for _ in range(EXAMENES_POR_CORRIDA)], EXAMENES_POR_CORRIDA)
        t["corr_dict"] = medir(lambda: [corregir_adecuada(tabla, respuestas)
                                        for _ in range(EXAMENES_POR_CORRIDA)], EXAMENES_POR_CORRIDA)

        def ranking_ingenua():
            notas = list(notas_base)          # la copia es O(n) en ambos lados: se copia igual
            for nota in nuevas:
                puesto_ingenua(notas, nota)

        arbol_base = SortedList(notas_base)

        def ranking_arbol():
            arbol_notas = arbol_base.copy()
            for nota in nuevas:
                puesto_adecuada(arbol_notas, nota)

        t["puesto_ing"] = medir(ranking_ingenua, NOTAS_POR_CORRIDA)
        t["puesto_arbol"] = medir(ranking_arbol, NOTAS_POR_CORRIDA)

        print(f"{n:>9,} | {t['armar_ing']:>11.3f} {t['armar_arbol']:>12.4f} | {t['corr_ing']:>11.2f} "
              f"{t['corr_arbol']:>12.4f} {t['corr_dict']:>11.4f} | {t['puesto_ing']:>12.3f} "
              f"{t['puesto_arbol']:>13.4f}")
        filas.append((n, t))
    return filas


def guardar_csv(filas, ruta="resultados.csv"):
    claves = list(filas[0][1])
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("n," + ",".join(f"{c}_ms" for c in claves) + "\n")
        for n, t in filas:
            f.write(f"{n}," + ",".join(f"{t[c]:.6f}" for c in claves) + "\n")
    print(f"\nGuardado en {ruta}")


if __name__ == "__main__":
    tamanos = tuple(int(x) for x in sys.argv[1:]) or TAMANOS
    print(f"Python {sys.version.split()[0]}\n")
    verificar(generar_banco(2_877))
    filas = correr(tamanos)
    if not sys.argv[1:]:
        guardar_csv(filas)
