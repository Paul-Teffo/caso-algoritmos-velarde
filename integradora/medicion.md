# Paul Steffano Velarde Chuquimia

# I3 · Medir: ingenuo (2^n) contra programación dinámica

## Protocolo

- **Carga:** se generan n útiles al azar con una semilla fija (`n + 1000`). Los costos van de 4 a 49 Bs y las utilidades de 10 a 99. El presupuesto es un tercio del costo total.
- **Tamaños:** n = 14, 16, 18 y 20. Para n = 20, la versión ingenua tarda aproximadamente 2 segundos, dentro del rango de 0,5 a 20 s.
- **Corridas:** se realiza una primera ejecución de calentamiento y luego 3 mediciones con `time.perf_counter()`. Se calcula el promedio.
- **Verificación:** ambas versiones pasan las 8 pruebas y obtienen la misma utilidad en los cuatro tamaños.

## Tabla de tiempos (ms)

| Versión | n | Presupuesto | Corrida 1 | Corrida 2 | Corrida 3 | Promedio | vs fila anterior | Utilidad |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Ingenua | 14 | 115 | 22,70 | 22,59 | 22,86 | 22,72 | — | 498 |
| Ingenua | 16 | 155 | 102,60 | 115,84 | 106,33 | 108,26 | x4,77 | 548 |
| Ingenua | 18 | 176 | 525,09 | 463,92 | 460,58 | 483,20 | x4,46 | 527 |
| Ingenua | 20 | 187 | 2 176,56 | 2 053,42 | 2 057,32 | 2 095,77 | x4,34 | 542 |
| Dinámica | 14 | 115 | 0,32 | 0,40 | 0,31 | 0,34 | — | 498 |
| Dinámica | 16 | 155 | 0,48 | 0,49 | 0,48 | 0,48 | x1,39 | 548 |
| Dinámica | 18 | 176 | 0,60 | 0,59 | 0,59 | 0,59 | x1,24 | 527 |
| Dinámica | 20 | 187 | 0,73 | 0,73 | 0,73 | 0,73 | x1,23 | 542 |

## Conclusión

- La versión ingenua es O(2^n · n): cada +2 útiles hay 4 veces más combinaciones. Lo medido fue x4,77, x4,46 y x4,34, cerca del ~4 esperado (un poco más porque también crece la n del ciclo interno).
- La programación dinámica es O(n · P). Sus tiempos están por debajo de 1 ms y crecen poco (x1,39, x1,24, x1,23), porque n y P crecen poco entre un tamaño y otro.
- Ambas versiones obtienen la misma utilidad en todos los casos, pero la dinámica consigue hacerlo en mucho menos tiempo.
- Hay ruido: en la ingenua, la corrida 1 de n = 18 dio 525 ms contra ≈ 461 ms de las otras dos; en la dinámica, la corrida 2 de n = 14 dio 0,40 contra 0,31. Con tiempos tan pequeños, cualquier variación del sistema pesa mucho, por eso los cocientes son aproximados.

## Dinámica con 1.000 útiles y presupuesto 10.000

| Corrida 1 | Corrida 2 | Corrida 3 | Promedio | Utilidad |
|---:|---:|---:|---:|---:|
| 2 478,79 ms | 2 612,79 ms | 2 472,41 ms | 2 521,33 ms | 35 040 |

Con 1.000 útiles y un presupuesto de 10.000 Bs, la programación dinámica tarda aproximadamente 2,5 segundos.

La tabla tiene 1.001 filas y 10.001 columnasmas o menos 10 millones de casillas

En cambio, la versión ingenua tendría que revisar 2^1000 combinaciones.

## ¿Y si el presupuesto fuera 1.000.000.000 de Bs?

La programación dinámica también depende del presupuesto. Si este aumenta demasiado, la tabla se vuelve muy grande.

Con 1.000 útiles y un presupuesto de 1.000 millones de Bs, se necesitarían aproximadamente 1 billón de casillas.

Esto requiere mucha memoria y haría que el programa no pudiera trabajar de forma práctica con esa tabla.

Por eso, la programación dinámica funciona bien cuando el presupuesto es manejable, pero deja de funcionar bien cuando es muy grande.
