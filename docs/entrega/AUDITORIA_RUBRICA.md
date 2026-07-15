# Auditoría frente al enunciado y la rúbrica

Fecha de revisión: 13 de julio de 2026.

Esta auditoría separa funcionalidad y evidencia de entrega. Una función
correcta no obtiene el máximo si la rúbrica exige además una captura, video o
sustentación.

## Resumen

| Criterio | Máximo | Estado defendible | Para llegar al máximo |
|---|---:|---:|---|
| 1. Branch and Bound | 8 | 5 | Falta una captura real del árbol actual en Gecode Gist. |
| 2. Formulación | 24 | 24 | Incluye parámetros, variables, restricciones, objetivo y uso de enteros. |
| 3. Modelo y pruebas | 48 | 48 | Conservar salidas, versiones y argumentos de eficiencia/optimalidad. |
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

- La ejecución reproducible con Gecode 6.3.0 reporta 50 nodos, 11 fallos,
  13 soluciones y profundidad máxima 18.
- La captura PNG disponible sólo muestra la raíz y no constituye evidencia
  del árbol. Por eso fue retirada del informe.
- Falta ejecutar Gecode Gist con el modelo y el DZN actuales, desplegar el
  árbol y guardar una captura que muestre el solver y sus estadísticas.

## 2. Formulación matemática

- [x] Parámetros \(n,m,p,v,c,ce,ct,maxM\), dominios y \(\sum p_i=n\).
- [x] Movimientos enteros \(x\), distribución \(y\), selección binaria \(z\)
  y producto linealizado \(q\).
- [x] Restricciones de dominio, diagonal, disponibilidad, balance,
  conservación, presupuesto, límite de movimientos y selección de mediana.
- [x] Objetivo de distancias absolutas a la mediana.
- [x] Identificación explícita como programación lineal entera.
- [x] Justificación de adecuación en ambos sentidos.

La mediana no necesita restricciones de posición adicionales: para cada
distribución final, minimizar sobre los valores \(v_k\) selecciona una mediana
ponderada. Esta justificación debe conservarse en el informe.

## 3. MiniZinc, pruebas y análisis

- [x] `Proyecto.mzn` implementa el modelo genérico.
- [x] El parser valida las \(7+m\) líneas de la sección 3.1 actualizada.
- [x] La entrada se lee como `.mpl` con matriz de costos antes de `ct`.
- [x] La conversión DZN conserva exactamente los decimales.
- [x] El DZN generado incluye `maxM` y el modelo restringe
  \(\sum |j-i|x_{i,j}\le maxM\).
- [x] Hay cinco instancias propias con entrada, DZN y óptimo.
- [x] La batería principal cubre diez configuraciones.
- [x] Se procesaron las 30 entradas suministradas: 28 válidas se resolvieron
  con optimalidad y pasaron las comprobaciones independientes; MinPol28 y
  MinPol29 se rechazaron porque declaran \(n=100\) y \(\sum p_i=125\).
- [x] Una verificación independiente recalcula restricciones, movimientos y
  objetivo.
- [x] El informe analiza bondades, falencias, eficiencia y optimalidad.
- [x] Se estudian tamaño, presupuesto y costo extra.
- [x] El resumen de la batería suministrada está en el informe y el detalle
  reproducible está en `Pruebas/resultados_bateria_suministrada.csv`.

Mejora recomendable: repetir los tiempos y reportar mediana y dispersión. Las
mediciones actuales son puntuales y el informe lo declara correctamente.

## 4. Sustentación

Cada integrante debería poder:

- derivar el costo escalado \(U_{i,j}\);
- explicar el conteo \(|j-i|\) usado por `maxM`;
- justificar balances y la linealización \(y_i z_k\);
- explicar por qué las desviaciones absolutas seleccionan una mediana;
- leer cota, incumbente, brecha y poda;
- defender el certificado de optimalidad;
- explicar una bondad, una falencia y el crecimiento \(O(m^2)\).

## 5. Interfaz

- [x] Lee MPL según la sección 3.1 actualizada.
- [x] Genera exactamente `DatosProyecto.dzn`.
- [x] Ejecuta `Proyecto.mzn`.
- [x] Muestra movimientos, distribución, costo, polarización, mediana y
  movimientos usados.
- [x] Muestra siete verificaciones de restricciones, incluida `maxM`.
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
- [ ] Árbol real exportado desde Gecode Gist con el modelo y DZN actuales.
- [ ] Video y enlace en el PDF.
- [ ] ZIP final con copia raíz de `Informe.pdf`.
