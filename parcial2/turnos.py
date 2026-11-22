# Paul Steffano Velarde chuquimia
import heapq
import sys
import time


class GestorIngenuo:
    def __init__(self):
        self._lista = []
        self._llegadas = 0

    def registrar(self, nombre, urgencia):
        self._lista.append((nombre, urgencia, self._llegadas))
        self._llegadas += 1

    def atender_siguiente(self):
        if not self._lista:
            return None
        mejor = 0
        for i in range(1, len(self._lista)):
            _, urg, lleg = self._lista[i]
            _, urg_m, lleg_m = self._lista[mejor]
            if urg < urg_m or (urg == urg_m and lleg < lleg_m):
                mejor = i
        return self._lista.pop(mejor)[0]

    def esta_esperando(self, nombre):
        for p in self._lista:
            if p[0] == nombre:
                return True
        return False

    @property
    def esperando(self):
        return len(self._lista)


class GestorMejorado:
    def __init__(self):
        self._heap = []
        self._en_espera = set()
        self._llegadas = 0

    def registrar(self, nombre, urgencia):
        heapq.heappush(self._heap, (urgencia, self._llegadas, nombre))
        self._en_espera.add(nombre)
        self._llegadas += 1

    def atender_siguiente(self):
        if not self._heap:
            return None
        _, _, nombre = heapq.heappop(self._heap)
        self._en_espera.discard(nombre)
        return nombre

    def esta_esperando(self, nombre):
        return nombre in self._en_espera

    @property
    def esperando(self):
        return len(self._en_espera)


GUION = [
    ("registrar", "Ana", 3, ""), ("registrar", "Beto", 1, ""),
    ("registrar", "Carla", 3, ""), ("registrar", "Diego", 2, ""),
    ("esperando", "", 0, "4"),
    ("esta", "Beto", 0, "True"), ("esta", "Zoe", 0, "False"),
    ("atender", "", 0, "Beto"), ("esta", "Beto", 0, "False"),
    ("atender", "", 0, "Diego"),
    ("registrar", "Elena", 1, ""),
    ("atender", "", 0, "Elena"), ("atender", "", 0, "Ana"), ("atender", "", 0, "Carla"),
    ("atender", "", 0, "(nadie)"), ("esperando", "", 0, "0"),
]


def ejecutar(gestor, op, arg, urg):
    if op == "registrar":
        gestor.registrar(arg, urg)
        return ""
    if op == "atender":
        nombre = gestor.atender_siguiente()
        return nombre if nombre is not None else "(nadie)"
    if op == "esta":
        return str(gestor.esta_esperando(arg))
    return str(gestor.esperando)


def probar(titulo, gestor):
    bien = total = 0
    for op, arg, urg, esperado in GUION:
        obtenido = ejecutar(gestor, op, arg, urg)
        if op == "registrar":
            continue
        total += 1
        if obtenido == esperado:
            bien += 1
        else:
            print(f"   MAL en «{op} {arg}»: esperado {esperado}, obtuvo {obtenido}")
    print(f"{titulo}: {bien} de {total} pasos correctos")
    return bien == total


def ejecutar_carga(gestor, n):
    for i in range(n):
        gestor.registrar(f"P{i}", (i * 7919) % 5 + 1)
    control = 0
    for _ in range(n):
        control += len(gestor.atender_siguiente())
    return control


def medir(clase, n, corridas=3):
    ejecutar_carga(clase(), n)
    tiempos = []
    for _ in range(corridas):
        inicio = time.perf_counter()
        ejecutar_carga(clase(), n)
        tiempos.append(time.perf_counter() - inicio)
    return tiempos


def main():
    ok = probar("GestorIngenuo ", GestorIngenuo())
    ok = probar("GestorMejorado", GestorMejorado()) and ok
    if not ok:
        sys.exit(1)

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2500
    tamanos = [n, 2 * n, 4 * n]

    for clase in (GestorIngenuo, GestorMejorado):
        control = ejecutar_carga(clase(), tamanos[0])
        print(f"\n{clase.__name__} (control n={tamanos[0]}: {control})")
        print("| n | corrida 1 (ms) | corrida 2 (ms) | corrida 3 (ms) | promedio (ms) | vs fila anterior |")
        print("|---:|---:|---:|---:|---:|---:|")
        anterior = None
        for tam in tamanos:
            tiempos = [t * 1000 for t in medir(clase, tam)]
            promedio = sum(tiempos) / len(tiempos)
            razon = f"x{promedio / anterior:.2f}" if anterior else "-"
            corridas = " | ".join(f"{t:.2f}" for t in tiempos)
            print(f"| {tam} | {corridas} | {promedio:.2f} | {razon} |")
            anterior = promedio


if __name__ == "__main__":
    main()
