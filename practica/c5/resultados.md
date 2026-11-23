# Resultados del torneo (promedio de 3 corridas, en milisegundos)

Python 3.14.3 · 3 corridas + 1 de calentamiento · enteros aleatorios (semilla 2026)

| Algoritmo | Orden | n = 10.000 | n = 20.000 | n = 40.000 | n = 80.000 |
|---|---|---:|---:|---:|---:|
| Insercion | O(n^2) | 1,944.40 | 7,649.37 | 34,344.02 | 206,691.44 |
| MergeSort | O(n log n) | 21.17 | 46.21 | 102.16 | 237.03 |
| QuickSort | O(n log n) | 15.79 | 34.81 | 73.94 | 166.04 |
| sort() Python | O(n log n) | 0.90 | 1.96 | 4.25 | 11.09 |

## Cuanto crece el tiempo al duplicar n (t(2n) / t(n))

Teorico: O(n^2) -> x4 · O(n log n) -> un poco mas de x2

| Algoritmo | 10.000→20.000 | 20.000→40.000 | 40.000→80.000 |
|---|---:|---:|---:|
| Insercion | x3.93 | x4.49 | x6.02 |
| MergeSort | x2.18 | x2.21 | x2.32 |
| QuickSort | x2.20 | x2.12 | x2.25 |
| sort() Python | x2.17 | x2.16 | x2.61 |
