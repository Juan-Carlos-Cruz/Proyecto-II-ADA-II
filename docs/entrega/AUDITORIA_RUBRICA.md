# Auditoría frente al enunciado y la rúbrica

Fecha de revisión: 1 de julio de 2026.

Esta auditoría separa funcionalidad y evidencia de entrega. Una función
correcta no obtiene el máximo si la rúbrica exige además una captura, video o
sustentación.

## Resumen

| Criterio | Máximo | Estado defendible | Para llegar al máximo |
|---|---:|---:|---|
| 1. Branch and Bound | 8 | 8 | Evidencia completa: explicación, caso pequeño y árbol real de Gecode Gist. |
| 2. Formulación | 24 | 24 | Mantener consistencia entre informe y MiniZinc. |
| 3. Modelo y pruebas | 48 | 48 | Conservar salidas y versiones para reproducibilidad. |
| 4. Sustentación | 10 | No evaluable todavía | Todos deben poder defender modelo, B&B, pruebas e interfaz. |
| 5. Interfaz | 10 | 2 sin video; 10 con el video correcto | Grabarlo, incluir a todos y poner el enlace en el PDF. |

El criterio 5 cae a 2 mientras no exista video porque la rúbrica asigna ese
nivel cuando hay interfaz pero no se entrega el video. La implementación sí
tiene capacidad para 10 puntos.

## 1. Branch and Bound

Evidencia existente:

- El informe explica incumbente, cota inferior, ramificación y causas de poda.
- Hay una instancia pequeña reproducible en
  `DatosProyecto/branch_and_bound/`.
- Se desarrollan costo, solución, cotas y cierre de brecha.
- Se reporta una ejecución mayor con Chuffed y sus métricas.

Evidencia del visualizador:

- Se ejecutó el ejemplo mayor con MiniZinc 2.9.7 y Gecode Gist 6.3.0.
- Gist reportó 23 nodos, ocho fallos, tres soluciones y profundidad máxima 14.
- El árbol se exportó directamente desde Gist a
  `docs/informe/assets/arbol_minizinc_instancia_mayor.pdf`.
- El informe incorpora su versión PNG y explica nodos de ramificación, hojas
  fallidas, soluciones y actualización de la cota incumbente.

## 2. Formulación matemática

- [x] Parámetros \(n,m,p,v,c,ce,ct\), dominios y \(\sum p_i=n\).
- [x] Movimientos enteros \(x\), distribución \(y\), selección binaria \(z\)
  y producto linealizado \(q\).
- [x] Restricciones de dominio, diagonal, disponibilidad, balance,
  conservación, presupuesto y selección de mediana.
- [x] Objetivo de distancias absolutas a la mediana.
- [x] Identificación explícita como programación lineal entera.
- [x] Justificación de adecuación en ambos sentidos.

La mediana no necesita restricciones de posición adicionales: para cada
distribución final, minimizar sobre los valores \(v_k\) selecciona una mediana
ponderada. Esta justificación debe conservarse en el informe.

## 3. MiniZinc, pruebas y análisis

- [x] `Proyecto.mzn` implementa el modelo genérico.
- [x] El parser valida las \(6+m\) líneas de la sección 3.1.
- [x] La conversión DZN conserva exactamente los decimales.
- [x] Hay cinco instancias propias con entrada, DZN y óptimo.
- [x] La batería cubre diez configuraciones.
- [x] Una verificación independiente recalcula restricciones y objetivo.
- [x] El informe analiza bondades, falencias, eficiencia y optimalidad.
- [x] Se estudian tamaño, presupuesto y costo extra.
- [ ] Si el campus publicó instancias adicionales a la del enunciado, deben
  agregarse a la tabla antes de entregar; no estaban entre los adjuntos
  auditados.

Mejora recomendable: repetir los tiempos y reportar mediana y dispersión. Las
mediciones actuales son puntuales y el informe lo declara correctamente.

## 4. Sustentación

Cada integrante debería poder:

- derivar el costo escalado \(U_{i,j}\);
- justificar balances y la linealización \(y_i z_k\);
- explicar por qué las desviaciones absolutas seleccionan una mediana;
- leer cota, incumbente, brecha y poda;
- defender el certificado de optimalidad;
- explicar una bondad, una falencia y el crecimiento \(O(m^2)\).

## 5. Interfaz

- [x] Lee PCA según la sección 3.1.
- [x] Genera exactamente `DatosProyecto.dzn`.
- [x] Ejecuta `Proyecto.mzn`.
- [x] Muestra movimientos, distribución, costo, polarización y mediana.
- [x] Muestra seis verificaciones de restricciones.
- [x] Presenta estadísticas, cota y salida técnica.
- [x] Ejecuta el solver sin bloquear la ventana.
- [ ] Falta el video enlazado desde el PDF.

El video debe durar máximo 15 minutos, incluir a todos, explicar los cinco
componentes del modelo y mostrar dos configuraciones en la interfaz.

## Portabilidad y Docker

Decisión: no usar Docker como método principal para la interfaz. Tkinter
requiere el sistema gráfico y diálogos nativos; Docker necesita mecanismos
distintos en X11, Wayland, Windows y macOS. Docker sería útil sólo para
pruebas de consola o integración continua. Para la demostración, las
instrucciones nativas y `ProyectoGUIFuentes/verificar_entorno.py` reducen más
el riesgo operativo.

## Conformidad con el enunciado

- [x] `Proyecto.mzn` en la raíz.
- [x] Directorios `DatosProyecto/`, `ProyectoGUIFuentes/` y `MisInstancias/`.
- [x] Cinco instancias con salida esperada.
- [x] La interfaz crea `DatosProyecto.dzn`.
- [x] Informe con modelo, implementación, B&B, pruebas, análisis y conclusiones.
- [x] Tres salidas factibles y óptimo del ejemplo.
- [x] Nombres, códigos, profesor y monitor en el informe.
- [x] Árbol real exportado desde Gecode Gist.
- [ ] Video y enlace en el PDF.
- [ ] ZIP final con copia raíz de `Informe.pdf`.
