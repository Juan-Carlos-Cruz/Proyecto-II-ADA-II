# Guion de sustentación — MinPol

Duración objetivo: **12 minutos**. La guía permite entre 12 y 15 minutos y
asigna 3 minutos a cada integrante. Este guion usa exactamente cuatro bloques
de 3 minutos. Los nombres corresponden al orden del informe; pueden
intercambiarse sin cambiar el contenido.

Las referencias “D1”, “D2”, etc. corresponden a las diapositivas de
`docs/presentacion/Presentacion_MinPol.pdf`.

## Reparto y cronómetro

| Tiempo | Responsable | Tema | Diapositivas |
|---|---|---|---|
| 0:00–3:00 | Juan Carlos Cruz Muñoz | Parámetros, variables y primera parte en MiniZinc | D1–D4 |
| 3:00–6:00 | David Alejandro Enciso Gutierrez | Restricciones, objetivo y resto en MiniZinc | D5–D8 |
| 6:00–9:00 | Juan Esteban Rodriguez Valencia | Resultados y análisis de pruebas | D9–D12 |
| 9:00–12:00 | Estiven Andres Martinez Granados | Dos pruebas en la aplicación y conclusiones | D13–D15 |

## 0:00–3:00 — Integrante 1: parámetros y variables

### 0:00–0:25 — D1. Apertura

> Buenos días. Somos Juan Carlos Cruz, David Enciso, Juan Esteban Rodriguez y
> Estiven Martinez. Presentamos MinPol, un modelo de programación entera lineal
> que decide cómo mover personas entre opiniones para minimizar la polarización
> de una población, respetando un presupuesto y un máximo de movimientos. La
> sustentación está dividida en cuatro partes de tres minutos.

### 0:25–0:55 — D2. ¿Qué problema resolvemos?

> Partimos de una población distribuida entre opiniones con valores numéricos.
> Una decisión traslada personas de una opinión inicial a otra. Esa decisión
> tiene costo y consume movimientos según la distancia entre los índices. El
> resultado que buscamos es una nueva distribución con la menor suma de
> distancias respecto de su mediana ponderada. No buscamos necesariamente
> consenso: buscamos la mejor distribución que sea factible.

### 0:55–1:50 — D3. Parámetros

> El conjunto de opiniones es O, desde 1 hasta m. El parámetro n es la población
> total y p sub i indica cuántas personas empiezan en la opinión i; por eso la
> suma de p debe ser n. Cada opinión tiene un valor v sub i entre cero y uno.
> La matriz c guarda el costo base de mover una persona de i a j. Además, ce sub
> j es un recargo cuando la opinión destino estaba vacía inicialmente. ct es el
> presupuesto disponible y maxM es la cantidad máxima de movimientos. Definimos
> e sub j como uno si p sub j era cero y como cero en otro caso. Así, el costo
> unitario efectivo es c sub i j por uno más p sub i sobre n, más e sub j por ce
> sub j. El recargo depende del estado inicial, no de lo que ocurra después.

### 1:50–2:35 — D4. Variables de decisión

> La variable principal x sub i j es entera y representa cuántas personas pasan
> del origen i al destino j. La variable y sub i contiene la población final en
> cada opinión. Para modelar la mediana introducimos z sub k, binaria: vale uno
> para el único valor de opinión elegido como mediana. Finalmente, q sub i k es
> una variable auxiliar que representará el producto entre y sub i y z sub k.
> Este producto se linealiza más adelante para mantener un modelo de
> programación entera lineal, llamado IP en el material y PLE en español.

### 2:35–3:00 — D4. Primera traducción a MiniZinc

> En `Proyecto.mzn`, los parámetros se declaran sobre el rango `1..m`; x, y y q
> tienen dominios enteros entre cero y n, y z entre cero y uno. Los costos y
> valores decimales llegan como enteros escalados. Con esto evitamos errores de
> punto flotante sin alterar las soluciones factibles. David continúa con las
> restricciones y la función objetivo.

## 3:00–6:00 — Integrante 2: restricciones y objetivo

### 3:00–3:45 — D5. Restricciones estructurales

> Primero fijamos x sub i i igual a cero, porque permanecer en la misma opinión
> no cuenta como movimiento. De cada origen no pueden salir más personas que las
> que estaban allí inicialmente. La distribución final se calcula como población
> inicial, menos salidas, más llegadas. También imponemos que la suma de y sea n.
> Aunque esta última igualdad se deduce del balance, hace explícita la
> conservación y ayuda a detectar errores. Como las personas que llegan no
> pueden volver a salir, cada persona se mueve a lo sumo una vez.

### 3:45–4:30 — D6. Presupuesto y máximo de movimientos

> Hay dos recursos diferentes. El presupuesto suma el costo unitario efectivo
> por cada x sub i j y exige que el total no exceda ct. Por separado, mover una
> persona de i a j consume el valor absoluto de j menos i. La suma de esas
> distancias, multiplicadas por x sub i j, no puede superar maxM. Por ejemplo,
> mover dos personas de la opinión 4 a la 1 cuesta seis movimientos, aunque sean
> solo dos personas. Presupuesto y movimientos pueden estar activos al mismo
> tiempo y ninguno reemplaza al otro.

### 4:30–5:20 — D7. Mediana, linealización y objetivo

> Elegimos exactamente una mediana con la suma de z igual a uno. El producto q
> igual a y por z no se escribe directamente. Usamos tres cotas con n como M
> grande: q es menor o igual que y, q es menor o igual que n por z, y q es mayor
> o igual que y menos n por uno menos z. Si z vale cero, q queda en cero; si
> vale uno, q queda igual a y. La función objetivo minimiza la suma de la
> distancia absoluta entre cada v sub i y el valor candidato v sub k,
> multiplicada por q sub i k. Para una distribución fija, minimizar desviaciones
> absolutas selecciona una mediana ponderada, incluso si los valores v no están
> ordenados.

### 5:20–6:00 — D8. Implementación y optimalidad

> MiniZinc usa exactamente estas secciones: movimientos, balance, costo,
> maxM, selección de mediana y objetivo. Para conservar decimales, el conversor
> multiplica costos y valores por potencias de diez y elimina la división por n;
> es una transformación algebraicamente equivalente. Luego un solver exacto
> aplica Branch and Bound, o ramificación y poda. La relajación lineal elimina
> temporalmente la integralidad y proporciona la cota inferior LB. La mejor
> solución entera factible es el incumbente y su valor proporciona la cota
> superior UB. Cuando LB y UB coinciden, la brecha es cero y el óptimo queda
> certificado. Juan Esteban presenta ahora la evidencia experimental.

## 6:00–9:00 — Integrante 3: resultados y análisis

### 6:00–6:35 — D9. Diseño de pruebas

> Evaluamos seis instancias principales, cuatro variaciones controladas y las
> treinta entradas suministradas. Además ejecutamos pruebas unitarias del parser,
> el escalamiento y la lectura de resultados. Un verificador independiente
> recalcula dominio, diagonal, disponibilidad, balance, población, costo,
> movimientos y polarización; es decir, no confía únicamente en el texto del
> solver. Todas las ejecuciones reportadas terminaron con estado óptimo.

### 6:35–7:20 — D10. Resultados principales

> En las seis instancias principales, HiGHS tardó entre aproximadamente 0.01 y
> 0.36 segundos. El ejemplo del enunciado obtuvo polarización 0.5 con costo 19.2
> y 14 movimientos. La instancia de consenso llegó a cero. La instancia cuatro
> fue la de mayor búsqueda, con 76 nodos, aunque solo tenía seis opiniones. La
> instancia cinco tenía ocho opiniones y necesitó 15 nodos. Esto muestra que el
> tamaño influye, pero la dificultad también depende de costos, simetrías y
> soluciones cercanas al óptimo. En la batería de treinta entradas, todas
> pasaron la verificación independiente y 23 valores coincidieron textualmente
> con la referencia; los otros siete difirieron solo en 0.001 por redondeo o
> truncamiento de la referencia.

### 7:20–8:10 — D11. Qué cambia el óptimo

> Al variar solo el presupuesto del ejemplo, la polarización baja de 4 con
> presupuesto cero, a 2 con diez, a 0.5 con veinte y a cero con veinticuatro.
> La curva nunca empeora al aumentar ct porque se amplía el conjunto factible,
> aunque cambia por escalones porque las personas son indivisibles. También
> aislamos el costo extra en la instancia tres: con recargo 12 en destinos
> centrales vacíos la polarización fue 6.75; al quitar el recargo bajó a 6. El
> límite maxM igual a 18 todavía impide aprovechar completamente el centro.

### 8:10–9:00 — D12. Eficiencia y Branch and Bound

> El modelo tiene dos familias cuadráticas principales: m al cuadrado variables
> x y m al cuadrado variables q, además de m binarias z. Por eso escalar en m es
> una limitación real. Sin embargo, los nodos no crecen monótonamente. Branch
> and Bound ramifica una variable fraccionaria para crear dos subproblemas. Un
> nodo se poda si su relajación es infactible o, en este problema de
> minimización, si su cota LB es mayor o igual que el UB del incumbente. Una
> solución entera actualiza el incumbente solo si lo mejora. En el ejemplo,
> HiGHS cerró la brecha en la raíz con presolve y cortes, mientras Chuffed mostró
> 225 nodos. Esas cifras no
> se contradicen: dependen del solver, sus heurísticas y su forma de contabilizar
> la búsqueda. Estiven cerrará con dos ejecuciones reproducibles.

## 9:00–12:00 — Integrante 4: dos pruebas y conclusiones

### 9:00–10:15 — D13. Prueba 1: ejemplo del enunciado

> Para la primera prueba cargo `DatosProyecto/ejemplos/ejemplo_pdf.mpl`, genero
> el DZN y resuelvo con HiGHS. La entrada tiene n igual a 20, cinco opiniones,
> presupuesto 20 y maxM 18. La aplicación devuelve la distribución final
> 18, 2, 0, 0, 0; costo 19.2; 14 movimientos; mediana cero y polarización 0.5.
> La matriz indica cuatro personas de la opinión 2 a la 1, dos de la 4 a la 1
> y dos de la 4 a la 2. El costo se reparte en 4.8, 9.6 y 4.8, para un total de
> 19.2. Los movimientos consumidos son 4, 6 y 4, para un total de 14. La
> población se conserva y las siete verificaciones de la interfaz aparecen
> aprobadas. Frente a la polarización inicial 4, la reducción es de 87.5 por
> ciento. Una enumeración independiente revisó 447 distribuciones finales
> factibles y confirmó que 0.5 es óptimo.

### 10:15–11:05 — D14. Prueba 2: consenso

> En la segunda prueba cargo `MisInstancias/instancia_01_consenso.mpl`. Aquí hay
> diez personas, cuatro opiniones, presupuesto 12 y maxM 6. El solver mueve tres
> personas de la opinión 3 a la 1. Como cada una recorre dos posiciones, usa
> exactamente los seis movimientos disponibles. El costo es 11.7, menor que 12.
> La distribución final queda 10, 0, 0, 0 y la polarización es cero. Este caso
> comprueba que el modelo identifica el consenso cuando existe una concentración
> completa que satisface simultáneamente presupuesto y maxM.

### 11:05–12:00 — D15. Conclusiones

> Concluimos cinco puntos. Primero, MinPol se representa exactamente como un
> modelo entero lineal mediante balance y una linealización de la mediana.
> Segundo, las restricciones conservan la población y controlan por separado el
> dinero y la distancia recorrida. Tercero, el escalamiento entero preserva los
> decimales sin cambiar el conjunto factible. Cuarto, el presupuesto, maxM y los
> costos extra modifican de forma visible la mejor polarización alcanzable.
> Quinto, la optimalidad no se asume: se certifica con una brecha de cero y se
> respalda con verificación independiente y treinta entradas suministradas. La
> principal limitación es el crecimiento cuadrático con el número de opiniones.
> En síntesis, la implementación entrega movimientos factibles, auditables y
> óptimos para las instancias evaluadas. Muchas gracias.

## Preparación antes de grabar

- Ensayar cada bloque con cronómetro; objetivo individual: entre 2:50 y 3:00.
- Reemplazar el nombre del responsable si el orden real del grupo cambia.
- Abrir previamente las dos rutas usadas en D13 y D14.
- Usar la presentación en modo pantalla completa y aumentar el tamaño de la GUI.
- En las demostraciones, mostrar los datos de entrada, pulsar “Generar DZN”,
  resolver y detenerse en el resumen y las siete verificaciones.
- No leer las ecuaciones símbolo por símbolo: explicar qué controla cada una.
- Ocultar notificaciones y datos personales.
- Confirmar que el archivo final no exceda 15 minutos.
- Agregar el enlace del video en `docs/informe/Informe.tex` y recompilar.
