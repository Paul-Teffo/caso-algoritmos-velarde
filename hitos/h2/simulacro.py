# Paul Steffano Velarde Chuquimia
import random
import time

K = 100
ELEGIDAS = [4, 5]
MATERIAS = [1, 2, 3, 4, 5]
PESOS = [1096, 664, 625, 346, 146]
TAMANOS = [5000, 10000, 20000, 40000]
SIMULACROS = 50


def generar_banco(n):
    random.seed(2026)
    banco = []
    for pid in range(1, n + 1):
        materia = random.choices(MATERIAS, weights=PESOS)[0]
        correcta = random.choice("ABCDE")
        banco.append((pid, materia, correcta))
    return banco


def responder(examen):
    respuestas = []
    for pid in examen:
        respuestas.append((pid, random.choice("ABCDE")))
    return respuestas


def armar_ingenua(banco, elegidas, k):
    candidatas = []
    for pid, materia, correcta in banco:
        if materia in elegidas:
            candidatas.append(pid)
    random.shuffle(candidatas)
    return candidatas[:k]


def corregir_ingenua(banco, respuestas):
    nota = 0
    for pid, marcada in respuestas:
        for p in banco:
            if p[0] == pid:
                if p[2] == marcada:
                    nota += 1
                break
    return nota


def preparar_elegida(banco):
    por_materia = {}
    correctas = {}
    for pid, materia, correcta in banco:
        if materia not in por_materia:
            por_materia[materia] = []
        por_materia[materia].append(pid)
        correctas[pid] = correcta
    return por_materia, correctas


def armar_elegida(por_materia, elegidas, k):
    candidatas = []
    for materia in elegidas:
        candidatas += por_materia[materia]
    return random.sample(candidatas, min(k, len(candidatas)))


def corregir_elegida(correctas, respuestas):
    nota = 0
    for pid, marcada in respuestas:
        if correctas[pid] == marcada:
            nota += 1
    return nota


def verificar():
    banco = generar_banco(2877)
    por_materia, correctas = preparar_elegida(banco)
    materia_de = {}
    for pid, materia, correcta in banco:
        materia_de[pid] = materia
    for examen in (armar_ingenua(banco, ELEGIDAS, K), armar_elegida(por_materia, ELEGIDAS, K)):
        assert len(examen) == K
        assert len(set(examen)) == K
        for pid in examen:
            assert materia_de[pid] in ELEGIDAS
    for _ in range(50):
        respuestas = responder(armar_elegida(por_materia, ELEGIDAS, K))
        assert corregir_ingenua(banco, respuestas) == corregir_elegida(correctas, respuestas)
    print("Verificación: las dos versiones dan el mismo resultado.")
    print()


def medir(trabajo):
    trabajo()
    total = 0
    for _ in range(3):
        inicio = time.perf_counter()
        trabajo()
        total += time.perf_counter() - inicio
    return total / 3 / SIMULACROS * 1000


def simulacros_ingenua(banco):
    for _ in range(SIMULACROS):
        examen = armar_ingenua(banco, ELEGIDAS, K)
        corregir_ingenua(banco, responder(examen))


def simulacros_elegida(por_materia, correctas):
    for _ in range(SIMULACROS):
        examen = armar_elegida(por_materia, ELEGIDAS, K)
        corregir_elegida(correctas, responder(examen))


def principal():
    print("Simulacro completo (armar 100 preguntas + corregir), ms por simulacro")
    print(f"{'n':>7} {'Ingenua':>10} {'Veces':>7} {'Elegida':>10} {'Veces':>7}")
    filas = []
    for n in TAMANOS:
        banco = generar_banco(n)
        por_materia, correctas = preparar_elegida(banco)
        ti = medir(lambda: simulacros_ingenua(banco))
        te = medir(lambda: simulacros_elegida(por_materia, correctas))
        if filas:
            vi = f"{ti / filas[-1][1]:.2f}"
            ve = f"{te / filas[-1][2]:.2f}"
        else:
            vi = ve = "-"
        print(f"{n:>7} {ti:>10.3f} {vi:>7} {te:>10.4f} {ve:>7}")
        filas.append((n, ti, te))
    print()
    return filas


def detalle():
    print("Detalle: cada operación por separado, ms por simulacro")
    print(f"{'n':>7} {'Armar ing.':>11} {'Armar eleg.':>12} {'Corr. ing.':>11} {'Corr. eleg.':>12}")
    for n in TAMANOS:
        banco = generar_banco(n)
        por_materia, correctas = preparar_elegida(banco)
        respuestas = responder(armar_elegida(por_materia, ELEGIDAS, K))
        a1 = medir(lambda: [armar_ingenua(banco, ELEGIDAS, K) for _ in range(SIMULACROS)])
        a2 = medir(lambda: [armar_elegida(por_materia, ELEGIDAS, K) for _ in range(SIMULACROS)])
        c1 = medir(lambda: [corregir_ingenua(banco, respuestas) for _ in range(SIMULACROS)])
        c2 = medir(lambda: [corregir_elegida(correctas, respuestas) for _ in range(SIMULACROS)])
        print(f"{n:>7} {a1:>11.3f} {a2:>12.4f} {c1:>11.3f} {c2:>12.4f}")
    print()


def guardar_csv(filas):
    with open("resultados.csv", "w", encoding="utf-8") as f:
        f.write("n,ingenua_ms,elegida_ms\n")
        for n, ti, te in filas:
            f.write(f"{n},{ti:.4f},{te:.5f}\n")


verificar()
filas = principal()
detalle()
guardar_csv(filas)
