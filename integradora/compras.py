# Paul Steffano Velarde Chuquimia
# Evaluación integradora · Variante B · Compras de una escuela
import random
import time


class Util:
    def __init__(self, codigo, costo_bs, utilidad):
        self.codigo = codigo
        self.costo_bs = costo_bs
        self.utilidad = utilidad


class CompradorIngenuo:
    def __init__(self):
        self._elegidos = []

    def elegir(self, utiles, presupuesto_bs):
        n = len(utiles)
        mejor = 0
        mejor_mascara = 0
        for mascara in range(1 << n):
            costo = 0
            utilidad = 0
            for i in range(n):
                if mascara & (1 << i):
                    costo += utiles[i].costo_bs
                    utilidad += utiles[i].utilidad
            if costo <= presupuesto_bs and utilidad > mejor:
                mejor = utilidad
                mejor_mascara = mascara
        self._elegidos = []
        for i in range(n):
            if mejor_mascara & (1 << i):
                self._elegidos.append(utiles[i].codigo)
        return mejor, list(self._elegidos)

    def esta_en_la_compra(self, codigo):
        return codigo in self._elegidos


class CompradorMejorado:
    def __init__(self):
        self._elegidos = set()

    def elegir(self, utiles, presupuesto_bs):
        n = len(utiles)
        t = [[0] * (presupuesto_bs + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            costo = utiles[i - 1].costo_bs
            valor = utiles[i - 1].utilidad
            for c in range(presupuesto_bs + 1):
                t[i][c] = t[i - 1][c]
                if costo <= c and t[i - 1][c - costo] + valor > t[i][c]:
                    t[i][c] = t[i - 1][c - costo] + valor

        self._elegidos = set()
        c = presupuesto_bs
        for i in range(n, 0, -1):
            if t[i][c] != t[i - 1][c]:
                self._elegidos.add(utiles[i - 1].codigo)
                c -= utiles[i - 1].costo_bs
        return t[n][presupuesto_bs], list(self._elegidos)

    def esta_en_la_compra(self, codigo):
        return codigo in self._elegidos


def lote(*datos):
    return [Util(c, costo, u) for c, costo, u in datos]


CASOS = [
    ("el voraz se equivoca", lote(("U1", 20, 120), ("U2", 40, 200), ("U3", 60, 240)), 100, 440, ["U2", "U3"]),
    ("cuatro útiles", lote(("U1", 4, 6), ("U2", 6, 8), ("U3", 8, 10), ("U4", 10, 12)), 16, 20, ["U2", "U4"]),
    ("presupuesto cero", lote(("U1", 5, 10), ("U2", 7, 12)), 0, 0, []),
    ("sin útiles", lote(), 30, 0, []),
    ("nada cabe", lote(("U1", 80, 90), ("U2", 100, 100)), 60, 0, []),
    ("entran todos", lote(("U1", 10, 20), ("U2", 14, 24), ("U3", 6, 8)), 200, 52, ["U1", "U2", "U3"]),
]


def probar(titulo, fabrica):
    bien = 0
    total = 0
    for que, utiles, presupuesto, esperada, codigos in CASOS:
        comprador = fabrica()
        utilidad, elegidos = comprador.elegir(utiles, presupuesto)
        total += 1
        if utilidad == esperada and sorted(elegidos) == sorted(codigos):
            bien += 1
        else:
            print(f"   MAL en «{que}»: esperado {esperada} con {codigos}, obtuvo {utilidad} con {elegidos}")
    c = fabrica()
    c.elegir(CASOS[0][1], CASOS[0][2])
    total += 2
    if c.esta_en_la_compra("U2"):
        bien += 1
    else:
        print("   MAL en «EstaEnLaCompra(U2)»: esperado True")
    if not c.esta_en_la_compra("U1"):
        bien += 1
    else:
        print("   MAL en «EstaEnLaCompra(U1)»: esperado False")
    print(f"{titulo}: {bien} de {total} pruebas correctas")


def ejecutar_carga(comprador, n, presupuesto=None):
    azar = random.Random(n + 1000)
    utiles = [Util("K" + str(i), azar.randint(4, 49), azar.randint(10, 99)) for i in range(n)]
    if presupuesto is None:
        presupuesto = sum(u.costo_bs for u in utiles) // 3
    utilidad, _ = comprador.elegir(utiles, presupuesto)
    return utilidad


def medir(fabrica, n, presupuesto=None):
    ejecutar_carga(fabrica(), n, presupuesto)
    tiempos = []
    utilidad = 0
    for _ in range(3):
        comprador = fabrica()
        inicio = time.perf_counter()
        utilidad = ejecutar_carga(comprador, n, presupuesto)
        tiempos.append((time.perf_counter() - inicio) * 1000)
    return tiempos, sum(tiempos) / 3, utilidad


def tabla(titulo, fabrica, tamanos):
    print(f"\n{titulo}")
    print(f"{'n':>4} {'corrida 1':>12} {'corrida 2':>12} {'corrida 3':>12} {'promedio ms':>12} {'x':>6} {'utilidad':>9}")
    anterior = 0
    utilidades = []
    for n in tamanos:
        t, prom, u = medir(fabrica, n)
        x = "—" if anterior == 0 else f"x{prom / anterior:.2f}"
        print(f"{n:>4} {t[0]:>12.2f} {t[1]:>12.2f} {t[2]:>12.2f} {prom:>12.2f} {x:>6} {u:>9}")
        anterior = prom
        utilidades.append(u)
    return utilidades


if __name__ == "__main__":
    probar("CompradorIngenuo ", CompradorIngenuo)
    probar("CompradorMejorado", CompradorMejorado)

    tamanos = [14, 16, 18, 20]
    u_ing = tabla("Ingenuo (2^n combinaciones)", CompradorIngenuo, tamanos)
    u_mej = tabla("Mejorado (programación dinámica)", CompradorMejorado, tamanos)
    print("\nMisma utilidad en los 4 tamaños:", u_ing == u_mej)

    t, prom, u = medir(CompradorMejorado, 1000, 10000)
    print(f"\nMejorado con 1.000 útiles y presupuesto 10.000: {[round(x, 2) for x in t]} ms · promedio {prom:.2f} ms · utilidad {u}")
