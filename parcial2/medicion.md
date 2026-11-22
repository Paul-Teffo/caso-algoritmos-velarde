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

-La ingenua es O(n²): porque tiene que buscar al siguiente paciente en cada atención. Al duplicar la cantidad de pacientes, el tiempo aumenta aproximadamente 4 veces, como se esperaba.

-La mejorada es O(n log n): utiliza el heap para organizar las atenciones. Al duplicar los pacientes, el tiempo aumenta aproximadamente entre 2 y 2,4 veces. También se nota que la diferencia frente a la ingenua aumenta cuando hay más pacientes.

-Ruido en las mediciones: los tiempos cambian un poco entre cada prueba, principalmente porque otros procesos de Windows pueden afectar las mediciones. Por eso se realizaron 3 pruebas y se calculó el promedio. A pesar de esas variaciones, la diferencia entre ambas soluciones sigue siendo bastante grande.
