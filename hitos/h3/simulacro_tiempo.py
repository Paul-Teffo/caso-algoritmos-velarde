# Paul Steffano Velarde Chuquimia
import random
import time

TAMANOS = [16, 18, 20, 22]


def generar_preguntas(n, tiempo_fijo=0):
    preguntas = []
    for i in range(n):
        if tiempo_fijo:
            tiempo = tiempo_fijo
        else:
            tiempo = random.randrange(50, 135, 5)
        valor = random.randint(1, 10)
        preguntas.append((tiempo, valor))
    total = 0
    for tiempo, valor in preguntas:
        total += tiempo
    limite = total // 2
    return preguntas, limite


def fuerza_bruta(preguntas, limite):
    n = len(preguntas)
    mejor = 0
    for combinacion in range(2 ** n):
        tiempo = 0
        valor = 0
        for i in range(n):
            if combinacion & (1 << i):
                tiempo += preguntas[i][0]
                valor += preguntas[i][1]
        if tiempo <= limite and valor > mejor:
            mejor = valor
    return mejor


def dinamica(preguntas, limite):
    n = len(preguntas)
    tabla = []
    for i in range(n + 1):
        tabla.append([0] * (limite + 1))
    for i in range(1, n + 1):
        tiempo, valor = preguntas[i - 1]
        for t in range(limite + 1):
            sin_ella = tabla[i - 1][t]
            if tiempo <= t:
                con_ella = tabla[i - 1][t - tiempo] + valor
            else:
                con_ella = 0
            tabla[i][t] = max(sin_ella, con_ella)
    return tabla[n][limite]


def voraz(preguntas, limite):
    ordenadas = sorted(preguntas, key=lambda p: p[1] / p[0], reverse=True)
    tiempo_usado = 0
    valor = 0
    for tiempo, v in ordenadas:
        if tiempo_usado + tiempo <= limite:
            tiempo_usado += tiempo
            valor += v
    return valor


def medir(funcion, preguntas, limite):
    funcion(preguntas, limite)
    total = 0
    for _ in range(3):
        inicio = time.perf_counter()
        funcion(preguntas, limite)
        total += time.perf_counter() - inicio
    return total / 3 * 1000


def contraejemplo():
    print("Contraejemplo (límite 120 s)")
    preguntas = [(70, 8), (60, 6), (60, 6)]
    print("  voraz:       ", voraz(preguntas, 120))
    print("  fuerza bruta:", fuerza_bruta(preguntas, 120))
    print("  dinámica:    ", dinamica(preguntas, 120))
    print()


def verificar():
    print("Verificación con 300 grupos de 12 preguntas al azar")
    random.seed(2026)
    distintas = 0
    falla_voraz = 0
    falla_voraz_fijo = 0
    for _ in range(300):
        preguntas, limite = generar_preguntas(12)
        optimo = fuerza_bruta(preguntas, limite)
        if dinamica(preguntas, limite) != optimo:
            distintas += 1
        if voraz(preguntas, limite) < optimo:
            falla_voraz += 1
        preguntas, limite = generar_preguntas(12, tiempo_fijo=60)
        if voraz(preguntas, limite) < fuerza_bruta(preguntas, limite):
            falla_voraz_fijo += 1
    print("  dinámica distinta de fuerza bruta:", distintas, "de 300")
    print("  voraz peor que el óptimo, tiempos distintos:", falla_voraz, "de 300")
    print("  voraz peor que el óptimo, 60 s fijos:", falla_voraz_fijo, "de 300")
    print()


def comparar():
    print("Fuerza bruta vs dinámica (ms, 1 calentamiento + 3 corridas)")
    print(f"{'n':>3} {'límite':>7} {'F. bruta':>10} {'Veces':>6} {'Dinámica':>9} {'Veces':>6} {'Óptimo':>7} {'Voraz':>6}")
    random.seed(2026)
    filas = []
    for n in TAMANOS:
        preguntas, limite = generar_preguntas(n)
        optimo = fuerza_bruta(preguntas, limite)
        assert dinamica(preguntas, limite) == optimo
        tb = medir(fuerza_bruta, preguntas, limite)
        td = medir(dinamica, preguntas, limite)
        if filas:
            vb = f"{tb / filas[-1][2]:.1f}"
            vd = f"{td / filas[-1][3]:.1f}"
        else:
            vb = vd = "-"
        print(f"{n:>3} {limite:>6}s {tb:>10.1f} {vb:>6} {td:>9.2f} {vd:>6} {optimo:>7} {voraz(preguntas, limite):>6}")
        filas.append((n, limite, tb, td, optimo, voraz(preguntas, limite)))
    print()
    return filas


def guardar_csv(filas):
    with open("resultados.csv", "w", encoding="utf-8") as f:
        f.write("n,limite_s,fuerza_bruta_ms,dinamica_ms,optimo,voraz\n")
        for n, limite, tb, td, optimo, valor_voraz in filas:
            f.write(f"{n},{limite},{tb:.2f},{td:.3f},{optimo},{valor_voraz}\n")


contraejemplo()
verificar()
filas = comparar()
guardar_csv(filas)
