"""
Práctica c3 — Tabla de mediciones de la búsqueda lineal O(n)
Protocolo: calentar, 5 corridas, promedio, con n, 4n y 16n.

Ejecutar:            python medicion.py
Elegir otro n:       python medicion.py 1000000
"""
import platform
import statistics
import sys
import time
from datetime import datetime

CALENTAR = 3
CORRIDAS = 5


def busqueda_lineal(lista, buscado):
    """Recorre uno por uno hasta encontrarlo. O(n)."""
    for i, x in enumerate(lista):
        if x == buscado:
            return i
    return -1


def medir(lista):
    buscado = -1  # peor caso: no está, recorre toda la lista

    # 1) Calentar (no se mide)
    for _ in range(CALENTAR):
        busqueda_lineal(lista, buscado)

    # 2) 5 corridas medidas
    tiempos = []
    for _ in range(CORRIDAS):
        inicio = time.perf_counter()
        busqueda_lineal(lista, buscado)
        fin = time.perf_counter()
        tiempos.append((fin - inicio) * 1000)  # a milisegundos

    # 3) Promedio
    return tiempos, statistics.mean(tiempos)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500_000
    tamanos = [n, 4 * n, 16 * n]

    filas = []
    anterior = None
    for tam in tamanos:
        print(f"Midiendo n = {tam:,} ...")
        lista = list(range(tam))
        tiempos, prom = medir(lista)
        ratio = f"x{prom / anterior:.2f}" if anterior else "—"
        corridas = " | ".join(f"{t:.3f}" for t in tiempos)
        filas.append(f"| {tam:,} | {corridas} | **{prom:.3f}** | {ratio} |")
        anterior = prom

    md = f"""# Práctica c3 — Tabla de mediciones: búsqueda lineal

- Lenguaje: Python {platform.python_version()}
- Máquina: {platform.processor() or platform.machine()} · {platform.system()} {platform.release()}
- Fecha: {datetime.now():%Y-%m-%d %H:%M}
- Protocolo: {CALENTAR} corridas de calentamiento, {CORRIDAS} corridas medidas, promedio. Peor caso (el elemento no está).

| n | Corrida 1 | Corrida 2 | Corrida 3 | Corrida 4 | Corrida 5 | Promedio (ms) | Ratio vs anterior |
|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(filas)}

## Análisis

Esperado: como la búsqueda lineal es O(n), al multiplicar n por 4 el tiempo debería multiplicarse por ~4.

Lo que vi: _(completar: ¿dio cerca de x4? si no, ¿qué pasó? ¿probaste con más datos?)_
"""
    with open("tabla.md", "w", encoding="utf-8") as f:
        f.write(md)

    print()
    print(md)
    print("✔ Tabla guardada en tabla.md")


if __name__ == "__main__":
    main()  