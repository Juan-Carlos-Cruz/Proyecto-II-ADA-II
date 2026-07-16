# Análisis de resultados

La tabla principal fue generada con MiniZinc 2.9.7 y HiGHS 1.14.0. La batería
de 30 entradas suministradas se ejecutó con COIN-BC 2.10.13, porque reproduce
el óptimo de referencia 10.313 de MinPol15. Los tiempos son mediciones
puntuales del solver; no incluyen la conversión del archivo ni el tiempo de
inicio de la interfaz. En todos los casos el solver cerró la búsqueda con
estado óptimo.

| Instancia | n | m | ct | maxM | Movs | Costo | Polarización | Tiempo (s) | Nodos | Estado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Ejemplo PDF | 20 | 5 | 20 | 18 | 14 | 19.2 | 0.5 | 0.0255 | 1 | Óptimo |
| Instancia 1 | 10 | 4 | 12 | 6 | 6 | 11.7 | 0 | 0.0121 | 1 | Óptimo |
| Instancia 2 | 20 | 5 | 10 | 7 | 7 | 9.8 | 5.8 | 0.1048 | 9 | Óptimo |
| Instancia 3 | 24 | 6 | 30 | 18 | 18 | 30 | 6.75 | 0.1867 | 11 | Óptimo |
| Instancia 4 | 18 | 6 | 18.75 | 15 | 14 | 18.6667 | 2.75 | 0.2588 | 76 | Óptimo |
| Instancia 5 | 40 | 8 | 45 | 25 | 24 | 44.85 | 11.7 | 0.3547 | 15 | Óptimo |

Además se procesaron las 30 entradas de `bateria_pruebas/mpl` con COIN-BC.
Todas se convirtieron a DZN, alcanzaron estado óptimo y pasaron la
comprobación independiente. `MinPol28.mpl` y `MinPol29.mpl` usan `n=125`,
consistente con su distribución inicial y con los valores de referencia del
profesor. El detalle reproducible está en
`Pruebas/resultados_bateria_suministrada.csv`.

De los 30 valores, 23 coinciden textualmente con la tabla del profesor y los
siete restantes difieren únicamente en 0.001. El modelo usa enteros escalados
y obtiene 9.687, 6.550, 14.172, 17.898, 23.567, 24.176 y 30.000; los valores
publicados son compatibles con truncamiento de representaciones flotantes.

## Efecto de aumentar m

El modelo contiene \(m^2\) variables de movimiento, \(m^2\) variables
auxiliares para la mediana y \(m\) variables de selección. Por ello, el
tamaño crece cuadráticamente con \(m\). En las pruebas HiGHS pasó de un nodo
en la instancia de cuatro opiniones a 15 nodos en la de ocho. Sin embargo,
la relación no es monótona: la instancia 4, con seis opiniones, necesitó 76
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
más que \(ct\) o requiere más movimientos que \(maxM\).

## Influencia de ce

La instancia 3 produce polarización 6.75 cuando las opiniones centrales
vacías tienen costo extra 12. Al repetirla con todos los costos extra en
cero, la polarización baja a 6. Sin el recargo aparece una mejora, pero el
límite \(maxM=18\) impide explotar por completo las opiniones centrales.
Esto confirma que el modelo aplica \(ce_j\) únicamente cuando \(p_j=0\)
inicialmente y que `maxM` puede ser la restricción activa junto al
presupuesto.

## Branch and Bound

En HiGHS, la instancia 4 produjo el mayor árbol de esta batería: 76 nodos.
La relajación lineal proporciona cotas inferiores; cada solución entera
factible establece una cota superior. Un nodo se poda si es infactible, si
su cota no mejora al incumbente o cuando ya es integral. El proceso termina
cuando la mejor cota coincide con el valor del incumbente.

Para el ejemplo, HiGHS resolvió el modelo en el nodo raíz después del
preprocesamiento. Chuffed mostró con más detalle la búsqueda discreta:
225 nodos, 114 fallos, 18 reinicios, profundidad máxima 9 y 17 198
propagaciones. Chuffed encontró polarización escalada 50 y luego demostró que
la restricción equivalente a buscar un valor menor o igual que 49 era
imposible. Estas cifras dependen del solver, sus heurísticas y la versión;
no son propiedades invariantes de la instancia.
