# Ejemplo pequeño de Branch and Bound

Esta instancia acompaña la explicación paso a paso del criterio 1 en el
informe.

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

El resultado esperado es objetivo escalado 10, cota 10, brecha 0, un nodo,
costo 3, 2 movimientos de 2 permitidos y polarización 1.

Para la evidencia interactiva solicitada por la rúbrica, abra el modelo y
una instancia en MiniZinc IDE y seleccione el solver `Gecode Gist`. La
captura debe mostrar el nombre del solver y el árbol; no debe reemplazarse
por el diagrama explicativo del informe.
