"""
H1 - Simulador de examenes de residencia medica
Medicion de la version actual (ingenua) contra la version de trabajo (optimizada).

Volumen real del sistema: 5 materias x 100 preguntas = 500 preguntas, 5 opciones c/u.

Protocolo del curso:
  calentar -> repetir -> promediar -> escalar -> mismas condiciones
  - CALENTAMIENTOS ejecuciones descartadas antes de medir
  - REPETICIONES ejecuciones medidas (media, desviacion, minimo)
  - se escala k (preguntas por examen) y U (usuarios en epoca de trafico)
  - ambas versiones usan la misma BD, los mismos indices, las mismas semillas
    y los mismos datos de entrada

Uso:
  python h1/benchmark.py            # corre todo y escribe h1/resultados.md y h1/resultados.csv
  python h1/benchmark.py --rapido   # menos repeticiones, para probar
"""
import argparse
import csv
import gc
import math
import os
import platform
import random
import sqlite3
import statistics
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

MATERIAS = 5
PREGUNTAS_POR_MATERIA = 100
OPCIONES_POR_PREGUNTA = 5
SEMILLA = 42

TAMANIOS_EXAMEN = [10, 50, 100, 200, 300, 400, 500]
USUARIOS = [1, 10, 50, 100, 200]
PREGUNTAS_POR_USUARIO = 100  # examen tipico en epoca de trafico

CARPETA = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Base de datos (equivalente a las tablas de Laravel: materias, preguntas,
# opciones, respuestas). Los indices de las claves foraneas existen en ambas
# versiones: la diferencia esta en el algoritmo, no en el esquema.
# ---------------------------------------------------------------------------
def crear_bd(ruta):
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.executescript(
        """
        CREATE TABLE materias(id INTEGER PRIMARY KEY, nombre TEXT);
        CREATE TABLE preguntas(id INTEGER PRIMARY KEY, materia_id INTEGER, enunciado TEXT);
        CREATE INDEX ix_preguntas_materia ON preguntas(materia_id);
        CREATE TABLE opciones(id INTEGER PRIMARY KEY, pregunta_id INTEGER, texto TEXT, es_correcta INTEGER);
        CREATE INDEX ix_opciones_pregunta ON opciones(pregunta_id);
        CREATE TABLE respuestas(id INTEGER PRIMARY KEY, intento_id INTEGER, pregunta_id INTEGER,
                                opcion_id INTEGER, correcta INTEGER);
        """
    )
    rng = random.Random(SEMILLA)
    nombres = ["Medicina interna", "Cirugia", "Pediatria", "Ginecologia y obstetricia", "Salud publica"]
    con.executemany("INSERT INTO materias VALUES (?, ?)", list(enumerate(nombres[:MATERIAS], start=1)))
    pregunta_id = opcion_id = 0
    for materia_id in range(1, MATERIAS + 1):
        for _ in range(PREGUNTAS_POR_MATERIA):
            pregunta_id += 1
            enunciado = f"Caso clinico {pregunta_id}: " + "x" * 300
            con.execute("INSERT INTO preguntas VALUES (?, ?, ?)", (pregunta_id, materia_id, enunciado))
            correcta = rng.randrange(OPCIONES_POR_PREGUNTA)
            for i in range(OPCIONES_POR_PREGUNTA):
                opcion_id += 1
                con.execute(
                    "INSERT INTO opciones VALUES (?, ?, ?, ?)",
                    (opcion_id, pregunta_id, f"Opcion {i + 1}: " + "y" * 80, int(i == correcta)),
                )
    con.commit()
    return con


# ---------------------------------------------------------------------------
# VERSION ACTUAL (ingenua) - reconstruccion de como lo hace el sistema hoy
# ---------------------------------------------------------------------------
def generar_examen_ingenuo(con, materias, k, rng):
    marcadores = ",".join("?" * len(materias))
    ids = [f[0] for f in con.execute(f"SELECT id FROM preguntas WHERE materia_id IN ({marcadores})", materias)]
    if k > len(ids):
        raise ValueError("k mayor que el banco disponible")

    # Sorteo con rechazo + "ya la elegi?" buscando en una lista: cada chequeo es O(k)
    # y cuando k se acerca a n se repiten muchos sorteos (n*H(n) intentos).
    elegidas = []
    while len(elegidas) < k:
        candidata = rng.choice(ids)
        if candidata not in elegidas:
            elegidas.append(candidata)

    # N+1: dos consultas por cada pregunta (como $pregunta->opciones sin eager loading)
    examen = []
    for pid in elegidas:
        enunciado = con.execute("SELECT enunciado FROM preguntas WHERE id = ?", (pid,)).fetchone()[0]
        opciones = con.execute(
            "SELECT id, texto, es_correcta FROM opciones WHERE pregunta_id = ?", (pid,)
        ).fetchall()
        examen.append({"id": pid, "enunciado": enunciado, "opciones": opciones})
    return examen


def corregir_ingenuo(con, intento_id, examen, respuestas):
    correctas = 0
    detalle = []
    for pid, opcion_id in respuestas:
        # busqueda lineal de la pregunta dentro del examen: O(k) por respuesta
        pregunta = None
        for p in examen:
            if p["id"] == pid:
                pregunta = p
                break
        # N+1: una consulta por respuesta para saber cual era la correcta
        correcta_id = con.execute(
            "SELECT id FROM opciones WHERE pregunta_id = ? AND es_correcta = 1", (pid,)
        ).fetchone()[0]
        ok = int(correcta_id == opcion_id)
        correctas += ok
        # un INSERT + COMMIT por respuesta
        con.execute(
            "INSERT INTO respuestas(intento_id, pregunta_id, opcion_id, correcta) VALUES (?, ?, ?, ?)",
            (intento_id, pid, opcion_id, ok),
        )
        con.commit()
        detalle.append((pregunta["enunciado"], opcion_id, correcta_id, ok))
    return correctas, detalle


# ---------------------------------------------------------------------------
# VERSION DE TRABAJO (optimizada)
# ---------------------------------------------------------------------------
class BancoEnCache:
    """El banco (500 preguntas) casi nunca cambia: se carga UNA vez con 2 consultas
    y se guarda en cache (en Laravel: Cache::rememberForever / Redis / APCu)."""

    def __init__(self, con):
        self.preguntas = {}
        ids_por_materia = defaultdict(list)
        for pid, materia_id, enunciado in con.execute("SELECT id, materia_id, enunciado FROM preguntas"):
            self.preguntas[pid] = {"id": pid, "enunciado": enunciado, "opciones": []}
            ids_por_materia[materia_id].append(pid)
        self.correcta = {}  # pregunta_id -> opcion correcta: tabla hash, consulta O(1)
        for oid, pid, texto, ok in con.execute(
            "SELECT id, pregunta_id, texto, es_correcta FROM opciones ORDER BY pregunta_id, id"
        ):
            self.preguntas[pid]["opciones"].append((oid, texto, ok))
            if ok:
                self.correcta[pid] = oid
        # 5 materias -> 31 combinaciones posibles: se precalcula el pool de cada una
        self.pools = {}
        materias = sorted(ids_por_materia)
        for r in range(1, len(materias) + 1):
            for combo in combinations(materias, r):
                self.pools[combo] = [pid for m in combo for pid in ids_por_materia[m]]

    def pool(self, materias):
        return self.pools[tuple(sorted(materias))]  # O(1)


def generar_examen_optimizado(banco, materias, k, rng):
    pool = banco.pool(materias)
    n = len(pool)
    if k > n:
        raise ValueError("k mayor que el banco disponible")
    # Fisher-Yates parcial: k intercambios, sin repetidos y sin rechazos -> O(k)
    for i in range(k):
        j = rng.randrange(i, n)
        pool[i], pool[j] = pool[j], pool[i]
    return [banco.preguntas[pid] for pid in pool[:k]]  # acceso por hash O(1) c/u


def corregir_optimizado(con, banco, intento_id, respuestas):
    correcta = banco.correcta
    filas = []
    detalle = []
    correctas = 0
    for pid, opcion_id in respuestas:
        ok = int(correcta[pid] == opcion_id)  # O(1)
        correctas += ok
        filas.append((intento_id, pid, opcion_id, ok))
        detalle.append((banco.preguntas[pid]["enunciado"], opcion_id, correcta[pid], ok))
    # un solo INSERT masivo y un solo COMMIT
    con.executemany(
        "INSERT INTO respuestas(intento_id, pregunta_id, opcion_id, correcta) VALUES (?, ?, ?, ?)", filas
    )
    con.commit()
    return correctas, detalle


# ---------------------------------------------------------------------------
# Utilidades de medicion
# ---------------------------------------------------------------------------
def responder(examen, rng):
    """El estudiante marca una opcion al azar en cada pregunta."""
    return [(p["id"], rng.choice(p["opciones"])[0]) for p in examen]


def limpiar_respuestas(con):
    con.execute("DELETE FROM respuestas")
    con.commit()


def medir(funcion, preparar, calentamiento, repeticiones):
    """preparar(rep) devuelve los argumentos; se ejecuta FUERA del cronometro."""
    for rep in range(calentamiento):
        funcion(*preparar(-1 - rep))
    tiempos = []
    for rep in range(repeticiones):
        args = preparar(rep)
        gc.collect()
        gc.disable()
        t0 = time.perf_counter()
        funcion(*args)
        t1 = time.perf_counter()
        gc.enable()
        tiempos.append((t1 - t0) * 1000)
    return {
        "media": statistics.mean(tiempos),
        "desv": statistics.stdev(tiempos) if len(tiempos) > 1 else 0.0,
        "min": min(tiempos),
    }


def exponente(t1, t2, x1, x2):
    """Pendiente en escala log-log: ~1 lineal, ~2 cuadratica, ~0 constante."""
    if t1 <= 0 or t2 <= 0:
        return float("nan")
    return math.log(t2 / t1) / math.log(x2 / x1)


def verificar(con, banco):
    """Antes de medir: ambas versiones deben dar la MISMA nota con la misma entrada."""
    rng = random.Random(SEMILLA)
    todas = list(range(1, MATERIAS + 1))
    examen = generar_examen_ingenuo(con, todas, 100, rng)
    respuestas = responder(examen, rng)
    nota_a, _ = corregir_ingenuo(con, 1, examen, respuestas)
    nota_b, _ = corregir_optimizado(con, banco, 2, respuestas)
    assert nota_a == nota_b, (nota_a, nota_b)
    examen_b = generar_examen_optimizado(banco, todas, 500, random.Random(SEMILLA))
    assert len({p["id"] for p in examen_b}) == 500  # sin repetidas
    limpiar_respuestas(con)


# ---------------------------------------------------------------------------
# Escenarios
# ---------------------------------------------------------------------------
def escenario_generacion(con, banco, cal, rep):
    todas = list(range(1, MATERIAS + 1))
    filas = []
    for k in TAMANIOS_EXAMEN:
        a = medir(lambda r: generar_examen_ingenuo(con, todas, k, r),
                  lambda i: (random.Random(SEMILLA + i),), cal, rep)
        b = medir(lambda r: generar_examen_optimizado(banco, todas, k, r),
                  lambda i: (random.Random(SEMILLA + i),), cal, rep)
        filas.append({"k": k, "consultas_a": 1 + 2 * k, "consultas_b": 0, "a": a, "b": b})
    return filas


def escenario_correccion(con, banco, cal, rep):
    todas = list(range(1, MATERIAS + 1))
    filas = []
    for k in TAMANIOS_EXAMEN:
        def preparar(i, k=k):
            limpiar_respuestas(con)
            rng = random.Random(SEMILLA + i)
            examen = generar_examen_optimizado(banco, todas, k, rng)
            return examen, responder(examen, rng)

        a = medir(lambda ex, resp: corregir_ingenuo(con, 1, ex, resp), preparar, cal, rep)
        b = medir(lambda _examen, resp: corregir_optimizado(con, banco, 1, resp), preparar, cal, rep)
        filas.append({"k": k, "consultas_a": 2 * k, "consultas_b": 1, "a": a, "b": b})
    limpiar_respuestas(con)
    return filas


def escenario_trafico(con, banco, cal, rep):
    """U usuarios rinden un examen de 100 preguntas de todas las materias:
    tiempo total de servidor para generar + corregir los U examenes."""
    todas = list(range(1, MATERIAS + 1))
    k = PREGUNTAS_POR_USUARIO

    def sesiones_ingenuas(U, rng):
        for u in range(U):
            examen = generar_examen_ingenuo(con, todas, k, rng)
            corregir_ingenuo(con, u, examen, responder(examen, rng))

    def sesiones_optimizadas(U, rng):
        for u in range(U):
            examen = generar_examen_optimizado(banco, todas, k, rng)
            corregir_optimizado(con, banco, u, responder(examen, rng))

    def preparar(i):
        limpiar_respuestas(con)
        return (random.Random(SEMILLA + i),)

    filas = []
    for U in USUARIOS:
        a = medir(lambda r: sesiones_ingenuas(U, r), preparar, cal, rep)
        b = medir(lambda r: sesiones_optimizadas(U, r), preparar, cal, rep)
        filas.append({"k": U, "consultas_a": U * (1 + 4 * k), "consultas_b": U, "a": a, "b": b})
    limpiar_respuestas(con)
    return filas


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------
def tabla_markdown(titulo, etiqueta, filas):
    lineas = [
        f"### {titulo}",
        "",
        f"| {etiqueta} | Consultas BD actual | Consultas BD optimizada | Actual media (ms) | Actual desv | "
        f"Optimizada media (ms) | Optimizada desv | Mejora (x) | Exponente actual | Exponente optimizada |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    previa = None
    for f in filas:
        if previa:
            ea = f"{exponente(previa['a']['media'], f['a']['media'], previa['k'], f['k']):.2f}"
            eb = f"{exponente(previa['b']['media'], f['b']['media'], previa['k'], f['k']):.2f}"
        else:
            ea = eb = "-"
        mejora = f["a"]["media"] / f["b"]["media"] if f["b"]["media"] > 0 else float("inf")
        lineas.append(
            f"| {f['k']} | {f['consultas_a']} | {f['consultas_b']} | {f['a']['media']:.3f} | {f['a']['desv']:.3f} | "
            f"{f['b']['media']:.3f} | {f['b']['desv']:.3f} | {mejora:,.1f} | {ea} | {eb} |"
        )
        previa = f
    return "\n".join(lineas) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rapido", action="store_true", help="1 calentamiento, 3 repeticiones")
    args = parser.parse_args()
    cal, rep = (1, 3) if args.rapido else (3, 10)
    cal_trafico, rep_trafico = (1, 2) if args.rapido else (2, 5)

    carpeta_tmp = tempfile.mkdtemp(prefix="h1_examenes_")
    con = crear_bd(os.path.join(carpeta_tmp, "examenes.sqlite"))

    t0 = time.perf_counter()
    banco = BancoEnCache(con)
    carga_cache_ms = (time.perf_counter() - t0) * 1000

    verificar(con, banco)

    print("Generacion del examen...", flush=True)
    gen = escenario_generacion(con, banco, cal, rep)
    print("Correccion al enviar...", flush=True)
    cor = escenario_correccion(con, banco, cal, rep)
    print("Epoca de trafico...", flush=True)
    tra = escenario_trafico(con, banco, cal_trafico, rep_trafico)
    con.close()

    entorno = (
        f"- Fecha: {datetime.now():%Y-%m-%d %H:%M}\n"
        f"- Python {platform.python_version()} ({platform.python_implementation()}), "
        f"SQLite {sqlite3.sqlite_version}\n"
        f"- Sistema: {platform.system()} {platform.release()} - {platform.machine()} - "
        f"{platform.processor() or 'CPU no informada'}\n"
        f"- Banco: {MATERIAS} materias x {PREGUNTAS_POR_MATERIA} preguntas x {OPCIONES_POR_PREGUNTA} opciones "
        f"(volumen real)\n"
        f"- Protocolo: {cal} calentamientos + {rep} repeticiones por medicion "
        f"(trafico: {cal_trafico} + {rep_trafico}); GC desactivado durante el cronometro; "
        f"mismas semillas y mismos datos para ambas versiones\n"
        f"- Carga inicial del banco a cache (una sola vez al desplegar): {carga_cache_ms:.2f} ms, 2 consultas\n"
    )
    md = (
        "# Tabla de mediciones - H1\n\n"
        "Generado por `python h1/benchmark.py`. Tiempos en milisegundos (media de las repeticiones).\n"
        "**Exponente** = pendiente log-log entre una fila y la anterior: ~0 constante, ~1 lineal, ~2 cuadratico.\n\n"
        f"## Condiciones\n\n{entorno}\n"
        "## Resultados\n\n"
        + tabla_markdown("1. Generar el examen (todas las materias)", "k preguntas", gen) + "\n"
        + tabla_markdown("2. Corregir al enviar (nota + correccion)", "k preguntas", cor) + "\n"
        + tabla_markdown(
            f"3. Epoca de trafico: U usuarios, examen de {PREGUNTAS_POR_USUARIO} preguntas (generar + corregir)",
            "U usuarios", tra)
        + "\n> SQLite es local (sin red). En el hosting, MySQL agrega ~0.2-1 ms de ida y vuelta por consulta,\n"
        "> asi que la version actual es en realidad MAS lenta de lo que muestra esta tabla: el costo de las\n"
        "> consultas N+1 aqui es un piso, no un techo.\n"
    )
    (CARPETA / "resultados.md").write_text(md, encoding="utf-8")

    with open(CARPETA / "resultados.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["escenario", "x", "version", "media_ms", "desv_ms", "min_ms", "consultas_bd"])
        for nombre, filas in (("generacion", gen), ("correccion", cor), ("trafico", tra)):
            for f in filas:
                for version, clave, consultas in (("actual", "a", f["consultas_a"]), ("optimizada", "b", f["consultas_b"])):
                    m = f[clave]
                    w.writerow([nombre, f["k"], version, f"{m['media']:.4f}", f"{m['desv']:.4f}",
                                f"{m['min']:.4f}", consultas])

    print(md)


if __name__ == "__main__":
    sys.exit(main())
