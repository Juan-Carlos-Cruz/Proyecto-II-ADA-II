# Guía rápida de uso

## Secuencia de la presentación

| Bloque | Tiempo | Diapositivas | Responsable |
|---|---:|---:|---|
| Parámetros y variables | 0:00–3:00 | 1–4 | Juan Carlos Cruz Muñoz (1824389) |
| Restricciones y objetivo | 3:00–6:00 | 5–8 | David Alejandro Enciso Gutierrez (2240581) |
| Resultados y análisis | 6:00–9:00 | 9–12 | Juan Esteban Rodriguez Valencia (2042282) |
| Dos pruebas y conclusiones | 9:00–12:00 | 13–15 | Estiven Andres Martinez Granados (2179687) |

Cada diapositiva incluye en el pie el responsable y el intervalo sugerido.
El discurso completo está en `../video/GuionVideo.md`.

## Correspondencia con el informe

| Sección del informe | Diapositivas | Uso en el video |
|---|---:|---|
| Introducción y descripción del problema | 1–2 | Contexto del primer bloque |
| Conjuntos, parámetros y variables | 3–4 | Primera parte del modelo formal y declaraciones MiniZinc |
| Restricciones, función objetivo e implementación | 5–8 | Segunda parte del modelo y restricciones MiniZinc |
| Pruebas realizadas y análisis de resultados | 9–12 | Resultados, sensibilidad, eficiencia y Branch and Bound |
| Ejemplo del enunciado e instancia de consenso | 13–14 | Dos pruebas reproducibles en la aplicación |
| Conclusiones | 15 | Cierre general del trabajo |

La presentación resume el informe sin introducir cifras nuevas: las tablas,
los gráficos, los resultados esperados y las conclusiones provienen de
`docs/informe/Informe.tex` y de los archivos de resultados verificados.

## Preparación de las pruebas en vivo

1. Abrir la aplicación con `python3 ProyectoGUIFuentes/app.py`.
2. Dejar localizados estos archivos:
   - `DatosProyecto/ejemplos/ejemplo_pdf.mpl`.
   - `MisInstancias/instancia_01_consenso.mpl`.
3. Para cada caso: cargar MPL, revisar los datos, generar DZN, elegir HiGHS y
   resolver.
4. Mostrar el resumen y las siete verificaciones aprobadas; no recorrer toda
   la salida técnica.

## Resultados que deben aparecer

| Prueba | Distribución final | Costo | Movimientos | Polarización |
|---|---|---:|---:|---:|
| Ejemplo del enunciado | `[18, 2, 0, 0, 0]` | 19.2 / 20 | 14 / 18 | 0.5 |
| Instancia de consenso | `[10, 0, 0, 0]` | 11.7 / 12 | 6 / 6 | 0 |

Si una ejecución tarda o aparece un problema de pantalla, continuar con la
captura de resultados incluida en las diapositivas 13 y 14.
