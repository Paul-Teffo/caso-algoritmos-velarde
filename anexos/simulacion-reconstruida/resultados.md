# Tabla de mediciones - H1

Generado por `python h1/benchmark.py`. Tiempos en milisegundos (media de las repeticiones).
**Exponente** = pendiente log-log entre una fila y la anterior: ~0 constante, ~1 lineal, ~2 cuadratico.

## Condiciones

- Fecha: 2026-11-08 23:29
- Python 3.14.3 (CPython), SQLite 3.50.4
- Sistema: Windows 11 - AMD64 - AMD64 Family 23 Model 160 Stepping 0, AuthenticAMD
- Banco: 5 materias x 100 preguntas x 5 opciones (volumen real)
- Protocolo: 3 calentamientos + 10 repeticiones por medicion (trafico: 2 + 5); GC desactivado durante el cronometro; mismas semillas y mismos datos para ambas versiones
- Carga inicial del banco a cache (una sola vez al desplegar): 4.57 ms, 2 consultas

## Resultados

### 1. Generar el examen (todas las materias)

| k preguntas | Consultas BD actual | Consultas BD optimizada | Actual media (ms) | Actual desv | Optimizada media (ms) | Optimizada desv | Mejora (x) | Exponente actual | Exponente optimizada |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 21 | 0 | 0.476 | 0.030 | 0.031 | 0.009 | 15.5 | - | - |
| 50 | 101 | 0 | 1.127 | 0.080 | 0.065 | 0.015 | 17.3 | 0.54 | 0.47 |
| 100 | 201 | 0 | 2.224 | 0.393 | 0.080 | 0.007 | 28.0 | 0.98 | 0.29 |
| 200 | 401 | 0 | 4.059 | 0.494 | 0.132 | 0.028 | 30.8 | 0.87 | 0.73 |
| 300 | 601 | 0 | 5.623 | 0.695 | 0.180 | 0.018 | 31.3 | 0.80 | 0.76 |
| 400 | 801 | 0 | 8.046 | 0.943 | 0.223 | 0.021 | 36.1 | 1.25 | 0.75 |
| 500 | 1001 | 0 | 17.606 | 2.382 | 0.404 | 0.234 | 43.6 | 3.51 | 2.67 |

### 2. Corregir al enviar (nota + correccion)

| k preguntas | Consultas BD actual | Consultas BD optimizada | Actual media (ms) | Actual desv | Optimizada media (ms) | Optimizada desv | Mejora (x) | Exponente actual | Exponente optimizada |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 20 | 1 | 0.896 | 0.975 | 0.187 | 0.048 | 4.8 | - | - |
| 50 | 100 | 1 | 2.829 | 2.859 | 0.217 | 0.018 | 13.1 | 0.71 | 0.09 |
| 100 | 200 | 1 | 3.588 | 2.482 | 0.360 | 0.186 | 10.0 | 0.34 | 0.73 |
| 200 | 400 | 1 | 8.165 | 3.452 | 0.501 | 0.051 | 16.3 | 1.19 | 0.48 |
| 300 | 600 | 1 | 13.013 | 4.128 | 0.676 | 0.100 | 19.2 | 1.15 | 0.74 |
| 400 | 800 | 1 | 18.257 | 3.902 | 0.876 | 0.216 | 20.9 | 1.18 | 0.90 |
| 500 | 1000 | 1 | 23.327 | 4.601 | 0.904 | 0.117 | 25.8 | 1.10 | 0.14 |

### 3. Epoca de trafico: U usuarios, examen de 100 preguntas (generar + corregir)

| U usuarios | Consultas BD actual | Consultas BD optimizada | Actual media (ms) | Actual desv | Optimizada media (ms) | Optimizada desv | Mejora (x) | Exponente actual | Exponente optimizada |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 401 | 1 | 4.936 | 0.821 | 0.402 | 0.031 | 12.3 | - | - |
| 10 | 4010 | 10 | 56.553 | 4.842 | 3.050 | 0.712 | 18.5 | 1.06 | 0.88 |
| 50 | 20050 | 50 | 281.678 | 9.807 | 13.271 | 2.100 | 21.2 | 1.00 | 0.91 |
| 100 | 40100 | 100 | 545.674 | 5.993 | 28.927 | 5.179 | 18.9 | 0.95 | 1.12 |
| 200 | 80200 | 200 | 1106.633 | 21.928 | 60.748 | 3.256 | 18.2 | 1.02 | 1.07 |

> SQLite es local (sin red). En el hosting, MySQL agrega ~0.2-1 ms de ida y vuelta por consulta,
> asi que la version actual es en realidad MAS lenta de lo que muestra esta tabla: el costo de las
> consultas N+1 aqui es un piso, no un techo.
