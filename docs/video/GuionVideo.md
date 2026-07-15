# Guion para el video explicativo

Duración objetivo: entre 12 y 14 minutos. El límite del enunciado es 15
minutos. Sustituir los nombres entre corchetes y redistribuir segmentos si el
grupo tiene menos de cuatro integrantes.

## 0:00–0:40 — Presentación

**[Integrante 1]**

- Presentar al grupo y la asignatura.
- Explicar que la aplicación minimiza la polarización bajo presupuesto y
  límite de movimientos.
- Mostrar brevemente la estructura de archivos.

## 0:40–2:20 — Problema MinPol

**[Integrante 1]**

- Explicar \(n,m,p,v,c,ce,ct,maxM\).
- Mostrar que cada decisión \(x_{i,j}\) mueve personas entre opiniones.
- Explicar el costo:

  \[
  c_{i,j}(1+p_i/n)x_{i,j}
  \]

  más \(ce_jx_{i,j}\) si el destino estaba vacío inicialmente.
- Explicar la polarización como suma de distancias a la mediana ponderada.
- Explicar que mover una persona de \(i\) a \(j\) consume \(|j-i|\)
  movimientos.

## 2:20–5:00 — Modelo matemático

**[Integrante 2]**

- Presentar variables \(x\), distribución final \(y\), selección de mediana
  \(z\) y auxiliares \(q\).
- Explicar las restricciones de salida máxima, balance, conservación,
  presupuesto y `maxM`.
- Señalar que se fija \(x_{i,i}=0\).
- Explicar brevemente la linealización \(q_{i,k}=y_i z_k\).
- Justificar que minimizar desviaciones absolutas selecciona una mediana.

## 5:00–6:30 — Implementación MiniZinc

**[Integrante 2]**

- Abrir `Proyecto.mzn`, sin leer código línea por línea.
- Mostrar las secciones de datos, movimientos, costo, límite `maxM`, mediana
  y salida.
- Explicar el escalamiento de decimales a enteros.
- Mencionar que el modelo fue probado con HiGHS, Chuffed y COIN-BC.

## 6:30–8:00 — Interfaz gráfica

**[Integrante 3]**

- Ejecutar `python3 ProyectoGUIFuentes/app.py`.
- Mostrar el botón “Cargar archivo .mpl”.
- Cargar el ejemplo del PDF y enseñar los datos validados.
- Elegir un solver.
- Presionar “Generar DatosProyecto.dzn” y luego “Resolver instancia”.
- Mostrar matriz, distribución, costo, movimientos usados, polarización,
  mediana y las siete verificaciones.

## 8:00–9:40 — Prueba 1: ejemplo del PDF

**[Integrante 3]**

- Usar `DatosProyecto/ejemplos/ejemplo_pdf.mpl`.
- Resultado esperado:
  - distribución `[18,2,0,0,0]`;
  - costo 19.2;
  - movimientos 14 de 18;
  - polarización 0.5;
  - mediana 0.
- Explicar los movimientos óptimos.
- Comparar brevemente con la polarización inicial 4.

## 9:40–11:10 — Prueba 2: consenso

**[Integrante 4]**

- Cargar `MisInstancias/instancia_01_consenso.mpl`.
- Mostrar que tres personas pasan de la opinión 3 a la 1.
- Resultado:
  - distribución `[10,0,0,0]`;
  - costo 11.7;
  - movimientos 6 de 6;
  - polarización 0.
- Explicar por qué polarización cero significa consenso.

## 11:10–12:30 — Resultados y Branch and Bound

**[Integrante 4]**

- Mostrar la tabla o los gráficos del informe.
- Explicar el efecto de elevar `ct`: 4, 2, 0.5 y 0 de polarización.
- Comparar la instancia 3 con y sin costos extra: 6.75 frente a 6, explicando
  que `maxM` también limita la mejora.
- Explicar que Branch and Bound poda por infactibilidad o por cota.
- Mencionar los 225 nodos observados con Chuffed en el ejemplo.

## 12:30–13:20 — Conclusiones

**Todos o [Integrante 1]**

- El modelo conserva la población y respeta presupuesto y `maxM`.
- La mediana quedó integrada mediante una formulación lineal.
- El escalamiento evita errores decimales.
- El presupuesto y los costos extra cambian de manera visible la solución.

## Lista de comprobación antes de grabar

- MiniZinc instalado y accesible desde `PATH`.
- La interfaz abre sin errores.
- Las dos instancias están localizadas previamente.
- Aumentar el tamaño de fuente de MiniZinc y de la interfaz.
- Ocultar notificaciones y datos personales.
- Cada integrante debe hablar.
- Confirmar que el video final dura menos de 15 minutos.
- Subir el video y pegar su enlace en `docs/informe/Informe.tex` antes de recompilar.
