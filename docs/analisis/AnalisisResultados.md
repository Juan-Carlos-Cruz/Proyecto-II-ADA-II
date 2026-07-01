# Análisis de resultados

Todas las ejecuciones fueron realizadas con MiniZinc 2.9.7 y HiGHS 1.14.0.
Los tiempos son mediciones puntuales del solver; no incluyen la conversión
del archivo ni el tiempo de inicio de la interfaz. En todos los casos el
solver reportó el mismo valor para la solución y su cota, por lo que el
estado es óptimo.

| Instancia | n | m | ct | Costo | Polarización | Tiempo (s) | Nodos | Estado |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Ejemplo PDF | 20 | 5 | 20 | 19.2 | 0.5 | 0.0263 | 1 | Óptimo |
| Instancia 1 | 10 | 4 | 12 | 11.7 | 0 | 0.0117 | 1 | Óptimo |
| Instancia 2 | 20 | 5 | 10 | 9.6 | 5.8 | 0.1391 | 3 | Óptimo |
| Instancia 3 | 24 | 6 | 30 | 30 | 6.75 | 0.1781 | 11 | Óptimo |
| Instancia 4 | 18 | 6 | 18.75 | 18.55 | 2.75 | 0.2128 | 72 | Óptimo |
| Instancia 5 | 40 | 8 | 45 | 44.95 | 11.7 | 0.4081 | 51 | Óptimo |

## Efecto de aumentar m

El modelo contiene \(m^2\) variables de movimiento, \(m^2\) variables
auxiliares para la mediana y \(m\) variables de selección. Por ello, el
tamaño crece cuadráticamente con \(m\). En las pruebas HiGHS pasó de un nodo
en la instancia de cuatro opiniones a 51 nodos en la de ocho. Sin embargo,
la relación no es monótona: la instancia 4, con seis opiniones, necesitó 72
nodos, más que la instancia 5. La dificultad también depende de la simetría,
los costos, la holgura presupuestaria y la cantidad de soluciones cercanas
al óptimo.

## Efecto del presupuesto

En el ejemplo, con \(ct=0\) la polarización es 4; con \(ct=10\) baja a 2;
con \(ct=20\) baja a 0.5; y con \(ct=24\) se alcanza consenso y la
polarización se vuelve 0. Aumentar el presupuesto no puede empeorar el
óptimo porque amplía el conjunto factible, aunque puede haber intervalos en
los que el valor no cambie debido a la integralidad de los movimientos.

## Consenso

La instancia 1 alcanza consenso con costo 11.7. El ejemplo también lo
alcanza al elevar el presupuesto a 24. En cambio, con el presupuesto
original 20 solo puede llegar a la distribución `[18,2,0,0,0]`. El consenso
no se alcanza cuando mover todas las personas hacia una sola opinión cuesta
más que \(ct\).

## Influencia de ce

La instancia 3 produce polarización 6.75 cuando las opiniones centrales
vacías tienen costo extra 12. Al repetirla con todos los costos extra en
cero, la polarización baja a 4.8. Sin el recargo, el solver utiliza las
opiniones centrales 3 y 4; con recargo, concentra población en opiniones que
ya estaban ocupadas. Esto confirma que el modelo aplica \(ce_j\) únicamente
cuando \(p_j=0\) inicialmente.

## Branch and Bound

En HiGHS, la instancia 4 produjo el mayor árbol de esta batería: 72 nodos.
La relajación lineal proporciona cotas inferiores; cada solución entera
factible establece una cota superior. Un nodo se poda si es infactible, si
su cota no mejora al incumbente o cuando ya es integral. El proceso termina
cuando la mejor cota coincide con el valor del incumbente.

Para el ejemplo, HiGHS resolvió el modelo en el nodo raíz después del
preprocesamiento. Chuffed mostró con más detalle la búsqueda discreta:
169 nodos, 83 fallos, 17 reinicios, profundidad máxima 8 y 13 480
propagaciones. Chuffed encontró polarización escalada 50 y luego demostró que
la restricción equivalente a buscar un valor menor o igual que 49 era
imposible. Estas cifras dependen del solver, sus heurísticas y la versión;
no son propiedades invariantes de la instancia.
