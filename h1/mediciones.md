# Mediciones del proceso actual - H1

Generado por `C:\xampp\php\php.exe h1\medir.php` el 2026-11-09 04:51.

## Condiciones

- XAMPP local: PHP 8.1.25, MariaDB 10.4.32-MariaDB (`innodb_flush_log_at_trx_commit=1`), Windows NT 10.0, AMD64 Family 23 Model 160 Stepping 0, AuthenticAMD
- Datos: copia de las tablas reales de `plataforma_med` (2877 preguntas, 5 materias)
- Se ejecutan las mismas consultas SQL que genera `SimulacroController` (`show` y `evaluar`); no se incluye el arranque de Laravel ni el render de la vista, así que el tiempo real es **mayor**
- Protocolo: 2 calentamientos + 10 repeticiones por punto; usuarios simultáneos: 3 repeticiones, procesos PHP en paralelo con arranque sincronizado

## 1. Escalando k (preguntas pedidas), todas las materias (n = 2877)

| k | Generar examen `show` (ms) | desv | Corregir `evaluar` (ms) | desv | Consultas en `evaluar` |
|---:|---:|---:|---:|---:|---:|
| 10 | 11,91 | 0,68 | 16,07 | 1,66 | 22 |
| 25 | 11,78 | 0,57 | 37,90 | 6,61 | 52 |
| 50 | 11,87 | 0,72 | 67,62 | 5,01 | 102 |
| 100 | 12,56 | 0,94 | 141,24 | 16,89 | 202 |
| 200 | 12,46 | 0,44 | 273,08 | 19,66 | 402 |
| 500 | 13,97 | 1,43 | 684,61 | 40,01 | 1002 |

## 2. Escalando n (preguntas de las materias elegidas), k = 100

| Materias | n | Generar examen `show` (ms) | desv |
|---|---:|---:|---:|
| Salud Pública | 146 | 6,19 | 0,55 |
| Salud Pública + Pediatría | 492 | 8,62 | 3,55 |
| Salud Pública + Pediatría + Ginecoobstetricia | 1156 | 9,79 | 2,40 |
| Medicina Interna + Ginecoobstetricia + Cirugia | 2385 | 12,62 | 0,56 |
| Salud Pública + Pediatría + Medicina Interna + Ginecoobstetricia + Cirugia | 2877 | 13,10 | 3,07 |

## 3. Usuarios simultáneos, examen de 100 preguntas (todas las materias)

| Usuarios | `show` media (ms) | `show` peor (ms) | `evaluar` media (ms) | `evaluar` peor (ms) | Consultas totales |
|---:|---:|---:|---:|---:|---:|
| 1 | 40,64 | 47,93 | 192,59 | 221,46 | 203 |
| 5 | 56,90 | 73,37 | 233,82 | 259,01 | 1015 |
| 10 | 103,42 | 113,45 | 313,99 | 366,17 | 2030 |
| 25 | 199,80 | 300,03 | 636,34 | 772,48 | 5075 |
| 50 | 319,35 | 449,16 | 1.377,50 | 1.655,11 | 10150 |
