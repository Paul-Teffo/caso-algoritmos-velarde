# Paul Steffano Velarde chuquimia

# P2.3 · Medir: lista simple contra heap + set

## Protocolo

- **Carga:** `ejecutar_carga(gestor, n)`, el port de `EjecutarCarga`. Llegan n pacientes con urgencia `(i·7919) % 5 + 1` y después se atiende a los n.
- **Tamaños que se duplican:** n = 2 500 · 5 000 · 10 000. Elegí n = 2 500 porque la ingenua, con el mayor tamaño, tarda 7,5 s, dentro del rango de 0,5 a 20 s. Con n = 4 000 la ingenua tardaba 22,6 s con 4n y quedaba fuera de ese rango.
- **Corridas:** 1 calentamiento (no se cuenta) + 3 corridas medidas con `time.perf_counter()` + promedio. Cada corrida usa un gestor nuevo.
- **Verificación antes de medir:** las dos versiones pasan 11 de 11 pasos del guion, incluido el desempate Ana/Carla. Las dos dan el mismo valor de control (11 390 con n = 2 500), así que atienden a los mismos pacientes.
- **Equipo:** Python 3.14.3, Windows 11. Comando: `python turnos.py` (imprime las pruebas y las tablas en consola).

## Tabla de tiempos (ms)

| Versión | n | corrida 1 | corrida 2 | corrida 3 | **promedio** | vs fila anterior |
|---|---:|---:|---:|---:|---:|---:|
| Ingenua (lista) | 2 500 | 396,44 | 429,87 | 370,86 | **399,06** | — |
| Ingenua (lista) | 5 000 | 1 677,28 | 1 879,12 | 1 677,84 | **1 744,75** | ×4,37 |
| Ingenua (lista) | 10 000 | 7 055,18 | 7 385,23 | 7 992,49 | **7 477,64** | ×4,29 |
| Heap + set | 2 500 | 2,27 | 2,26 | 3,11 | **2,55** | — |
| Heap + set | 5 000 | 6,95 | 6,28 | 5,25 | **6,16** | ×2,42 |
| Heap + set | 10 000 | 14,91 | 12,65 | 11,68 | **13,08** | ×2,12 |

Con n = 10 000, la ingenua tarda **≈ 570 veces más** que la mejorada (7 477,64 / 13,08).

## Conclusión

- **La ingenua se comporta como O(n²)** (n atenciones de O(n) cada una). Al duplicar n el tiempo se multiplica por ≈ 4,3, cerca del ×4 esperado. El poco de más se explica porque `pop(i)` también mueve elementos y porque la lista ya no cabe tan bien en la caché.
- **La mejorada se comporta como O(n log n)** (n operaciones de O(log n) cada una). Al duplicar n el tiempo se multiplica por ≈ 2,1–2,4, cerca del ×2,1 esperado. La brecha con la ingenua crece con n: ×156 con n = 2 500 y ×570 con n = 10 000.
- **Ruido:** dentro de cada fila las corridas varían hasta un 30 % en la mejorada (2,26 a 3,11 ms) y un 13 % en la ingenua (7 055 a 7 992 ms), por otros procesos de Windows y por el recolector de basura de Python. Con tiempos de pocos ms el ruido pesa más, así que el ×2,42 de la mejorada no indica un crecimiento peor que n log n. Por eso se promedian 3 corridas después del calentamiento. Aun así, el ruido no cambia la conclusión: las diferencias medidas son de dos órdenes de magnitud.
