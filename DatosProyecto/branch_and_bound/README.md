# Ejemplo pequeño de Branch and Bound

Esta instancia acompaña la explicación paso a paso del criterio 1 en el
informe. Se diseñó para que la relajación lineal clásica tenga una solución
fraccionaria y permita mostrar explícitamente la ramificación y la poda.

Conversión:

```bash
python3 ProyectoGUIFuentes/convertir_mpl.py \
  DatosProyecto/branch_and_bound/ejemplo_pequeno.mpl \
  DatosProyecto/branch_and_bound/ejemplo_pequeno.dzn
```

Ejecución reproducible:

```bash
minizinc --solver HiGHS --statistics --verbose \
  Proyecto.mzn DatosProyecto/branch_and_bound/ejemplo_pequeno.dzn
```

El resultado entero esperado es objetivo escalado 10, cota 10, brecha 0,
costo 3, 2 movimientos de 4 permitidos y polarización 1. El solver puede
cerrar el problema en la raíz mediante presolve y cortes; el informe presenta
por separado el árbol del Branch and Bound clásico sobre la relajación:

- raíz: \((a,b)=(2,1/6)\), con \(LB=11/12\);
- rama \(b\le 0\): solución entera \((2,0)\), con \(UB=1\);
- rama \(b\ge 1\): \((1/3,1)\), con \(LB=4/3\), podada por cota.

Para la evidencia interactiva solicitada por la rúbrica, abra el modelo y
una instancia en MiniZinc IDE y seleccione el solver `Gecode Gist`. La
captura debe mostrar el nombre del solver y el árbol; no debe reemplazarse
por el diagrama explicativo del informe.
