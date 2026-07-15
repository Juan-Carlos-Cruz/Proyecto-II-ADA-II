# Modelo matemático para MinPol

## 1. Conjuntos e índices

Sea \(O=\{1,\ldots,m\}\) el conjunto de opiniones posibles. Los índices
\(i,j,k\in O\) representan, respectivamente, una opinión de origen, una
opinión de destino y una opinión candidata para la mediana.

## 2. Parámetros

- \(n\in\mathbb{N}\): número total de personas.
- \(m\in\mathbb{N}\): número de opiniones posibles.
- \(p_i\in\{0,\ldots,n\}\): personas que inicialmente tienen la opinión
  \(i\).
- \(v_i\in[0,1]\): valor numérico de la opinión \(i\).
- \(c_{i,j}\in\mathbb{R}_{\ge 0}\): costo base de mover una persona desde
  la opinión \(i\) hasta la opinión \(j\).
- \(ce_j\in\mathbb{R}_{\ge 0}\): costo adicional por persona cuando la
  opinión de destino \(j\) estaba vacía inicialmente.
- \(ct\in\mathbb{R}_{\ge 0}\): presupuesto máximo.
- \(maxM\in\mathbb{N}^{+}\): máximo número de movimientos permitidos.

Los datos válidos deben satisfacer:

\[
\sum_{i\in O}p_i=n.
\]

El indicador constante

\[
e_j =
\begin{cases}
1,&p_j=0,\\
0,&p_j>0
\end{cases}
\]

permite representar el costo extra. Es un parámetro, no una variable,
porque el enunciado se refiere a una opinión vacía en la distribución
inicial.

El costo unitario efectivo de mover una persona de \(i\) a \(j\) es:

\[
a_{i,j}=c_{i,j}\left(1+\frac{p_i}{n}\right)+e_jce_j.
\]

## 3. Variables de decisión

- \(x_{i,j}\in\{0,\ldots,n\}\): personas que pasan de la opinión inicial
  \(i\) a la opinión \(j\).
- \(y_i\in\{0,\ldots,n\}\): personas con opinión \(i\) después de los
  movimientos.
- \(z_k\in\{0,1\}\): vale 1 cuando \(v_k\) es el valor seleccionado como
  mediana ponderada.
- \(q_{i,k}\in\{0,\ldots,n\}\): variable auxiliar que representa el
  producto \(y_i z_k\).

Se fija \(x_{i,i}=0\), pues permanecer en la misma opinión no es un
movimiento.

## 4. Restricciones

### 4.1. Selección de movimientos

No pueden salir de una opinión más personas de las que pertenecían
inicialmente a ella:

\[
\sum_{\substack{j\in O\\j\ne i}}x_{i,j}\le p_i
\qquad \forall i\in O.
\]

Esta restricción también asegura que cada persona se mueve a lo sumo una
vez: las personas que llegan a una opinión no pueden volver a salir como
parte de otro movimiento.

### 4.2. Distribución final

\[
y_i =
p_i
-\sum_{\substack{j\in O\\j\ne i}}x_{i,j}
+\sum_{\substack{j\in O\\j\ne i}}x_{j,i}
\qquad \forall i\in O.
\]

Además:

\[
\sum_{i\in O}y_i=n.
\]

Esta última igualdad es redundante respecto de las ecuaciones de balance,
pero se conserva para hacer explícita la conservación de la población y
detectar errores en modificaciones futuras del modelo.

### 4.3. Presupuesto

\[
\sum_{i\in O}\sum_{\substack{j\in O\\j\ne i}}
a_{i,j}x_{i,j}\le ct.
\]

Sustituyendo \(a_{i,j}\):

\[
\sum_{i\in O}\sum_{\substack{j\in O\\j\ne i}}
\left[
c_{i,j}\left(1+\frac{p_i}{n}\right)+e_jce_j
\right]x_{i,j}
\le ct.
\]

### 4.4. Límite de movimientos

El enunciado cuenta mover una persona de la opinión \(i\) a la opinión
\(j\) como \(|j-i|\) movimientos. Por tanto:

\[
\sum_{i\in O}\sum_{\substack{j\in O\\j\ne i}}
|j-i|x_{i,j}\le maxM.
\]

### 4.5. Selección y linealización de la mediana

Se selecciona exactamente un valor candidato:

\[
\sum_{k\in O}z_k=1.
\]

El producto \(q_{i,k}=y_i z_k\) se linealiza usando \(n\) como cota
superior válida para \(y_i\):

\[
\begin{aligned}
q_{i,k} &\le y_i,\\
q_{i,k} &\le nz_k,\\
q_{i,k} &\ge y_i-n(1-z_k)
\end{aligned}
\qquad \forall i,k\in O.
\]

Como \(q_{i,k}\ge0\), estas restricciones fuerzan \(q_{i,k}=y_i\) si
\(z_k=1\), y \(q_{i,k}=0\) si \(z_k=0\).

## 5. Función objetivo

La polarización linealizada es:

\[
P=\sum_{i\in O}\sum_{k\in O}|v_i-v_k|q_{i,k}.
\]

El modelo resuelve:

\[
\min P.
\]

Para cualquier distribución final fija \(y\), minimizar
\(\sum_i y_i|v_i-v_k|\) respecto de \(k\) selecciona una mediana ponderada.
Por tanto, no hace falta imponer por separado restricciones de balance a
ambos lados de la mediana. En poblaciones pares puede existir un intervalo
completo de medianas; al menos uno de sus extremos es un valor \(v_k\), y
produce la misma suma de desviaciones absolutas.

Esta formulación tampoco requiere que los valores \(v_i\) estén ordenados.

## 6. Escalamiento exacto usado en MiniZinc

Los archivos `.dzn` representan los costos y valores de opinión como
enteros escalados:

- \(V_i=S_vv_i\);
- \(C_{i,j}=S_cc_{i,j}\);
- \(CE_j=S_cce_j\);
- \(CT=S_cct\).

Los factores \(S_v\) y \(S_c\) son potencias de diez elegidas al convertir
el archivo `.mpl`. Así se preservan exactamente todos los decimales finitos
de la entrada.

Para evitar la división por \(n\), el costo se multiplica por \(nS_c\):

\[
U_{i,j}=C_{i,j}(n+p_i)+e_jCE_jn.
\]

La restricción equivalente usada por MiniZinc es:

\[
\sum_{i,j:i\ne j}U_{i,j}x_{i,j}\le CTn.
\]

El parámetro \(maxM\) y el conteo \(|j-i|x_{i,j}\) ya son enteros, por lo
que se usan directamente en MiniZinc.

La polarización escalada es:

\[
P_s=\sum_{i,k}|V_i-V_k|q_{i,k}=S_vP.
\]

El escalamiento no modifica el conjunto de soluciones factibles ni el
orden de los valores de la función objetivo.

## 7. Justificación de adecuación

Las variables \(x\) describen directamente la salida exigida por MinPol.
Las restricciones de salida y balance impiden crear personas, perderlas o
mover más personas de las disponibles inicialmente. La restricción de
presupuesto reproduce el costo definido en el enunciado, incluido el costo
extra por destinos inicialmente vacíos. La restricción de movimientos limita
la distancia total recorrida por las personas movidas, tal como lo define el
enunciado actualizado. Finalmente, la función objetivo
calcula la suma de distancias a una mediana ponderada de la distribución
final. En consecuencia, toda asignación factible de movimientos representa
una solución válida de MinPol y viceversa. La variable de selección puede
escoger cualquier opinión candidata en una solución factible; al optimizar,
la función objetivo fuerza que la candidata seleccionada sea una mediana
ponderada y que la polarización sea mínima.
