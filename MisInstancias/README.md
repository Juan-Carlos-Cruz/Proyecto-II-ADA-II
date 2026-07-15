# Cinco instancias propuestas

Cada instancia incluye el archivo de entrada `.mpl`, su conversión `.dzn` y
un archivo `.resultado.txt` con una solución cuyo óptimo fue certificado por
HiGHS. La igualdad entre `objective` y `objectiveBound` fue comprobada en
cada ejecución.

## 1. `instancia_01_consenso`

Instancia pequeña con dos opiniones inicialmente pobladas. El presupuesto
permite mover las tres personas de la opinión 3 a la opinión 1.

- \(n=10\), \(m=4\), \(ct=12\), \(maxM=6\).
- Costo usado: 11.7.
- Movimientos usados: 6.
- Polarización óptima: 0.
- Propósito: comprobar que el modelo identifica cuándo se puede alcanzar
  consenso.

## 2. `instancia_02_presupuesto_limitado`

Distribución con población en ambos extremos y presupuesto insuficiente para
consenso.

- \(n=20\), \(m=5\), \(ct=10\), \(maxM=7\).
- Costo usado: 9.8.
- Movimientos usados: 7.
- Polarización óptima: 5.8.
- Propósito: comprobar una solución parcial y un cambio de mediana.

## 3. `instancia_03_costos_extra_altos`

Las dos opiniones centrales están inicialmente vacías y tienen costo extra
12. Esto desincentiva utilizarlas aunque geométricamente resulten atractivas.

- \(n=24\), \(m=6\), \(ct=30\), \(maxM=18\).
- Costo usado: 30.
- Movimientos usados: 18.
- Polarización óptima: 6.75.
- Propósito: evaluar la condición \(p_j=0\) del costo extra.

## 4. `instancia_04_costos_decimales`

Todos los grupos tienen igual tamaño y tanto costos como presupuesto incluyen
decimales.

- \(n=18\), \(m=6\), \(ct=18.75\), \(maxM=15\).
- Costo usado: 18.6667.
- Movimientos usados: 14.
- Polarización óptima: 2.75.
- Propósito: verificar el escalamiento entero exacto y generar una búsqueda
  con más nodos.

## 5. `instancia_05_grande`

Instancia de mayor tamaño con ocho opiniones, dos opiniones inicialmente
vacías y población en ambos extremos.

- \(n=40\), \(m=8\), \(ct=45\), \(maxM=25\).
- Costo usado: 44.85.
- Movimientos usados: 24.
- Polarización óptima: 11.7.
- Propósito: aumentar el número de variables y comparar el comportamiento de
  los solvers.

## Reproducción

Desde la raíz del proyecto:

```bash
python3 ProyectoGUIFuentes/convertir_mpl.py \
    MisInstancias/instancia_01_consenso.mpl \
    MisInstancias/instancia_01_consenso.dzn

minizinc --solver HiGHS --statistics \
    Proyecto.mzn MisInstancias/instancia_01_consenso.dzn
```
