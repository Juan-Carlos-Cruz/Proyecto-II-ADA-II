# Guía para actualizar la captura de Gecode Gist

Esta evidencia corresponde al criterio 1 de la rúbrica. Debe hacerse con el
modelo actualizado, es decir, usando la instancia `.mpl` ya convertida a
`DatosProyecto/ejemplos/ejemplo_pdf.dzn` y la restricción `maxM`.

## 1. Abrir Gist

Desde la raíz del proyecto:

```bash
./docs/scripts/abrir_gist.sh
```

Si el script no encuentra MiniZinc, ejecutar con la ruta instalada:

```bash
MINIZINC_EXECUTABLE=/home/juan-carlos-cruz/.local/opt/minizinc-2.9.7/bin/minizinc \
  ./docs/scripts/abrir_gist.sh
```

## 2. Completar la búsqueda

En la ventana de Gecode Gist:

- Ejecutar la búsqueda hasta que no queden nodos abiertos.
- Verificar que la ventana corresponda a `Gecode Gist 6.3.0`.
- La solución óptima esperada tiene polarización `50/100`, distribución
  `[18, 2, 0, 0, 0]`, costo `384/20` y `TOTAL_MOVIMIENTOS=14`.

Como referencia del backend Gecode sin visualizador, la ejecución actual del
modelo reportó 50 nodos, 11 fallos, 13 soluciones y profundidad máxima 18.
La captura final de Gist muestra profundidad visual 19, 13 nodos solución,
17 fallidos, 29 de ramificación y cero abiertos. La diferencia corresponde a
que el visualizador cuenta las categorías dibujadas y el backend reporta
eventos internos de búsqueda.

## 3. Guardar la evidencia

Opción preferida:

- Usar la opción de exportar/guardar imagen de Gist, si aparece en el menú.
- Guardar la imagen como:
  `docs/informe/assets/arbol_minizinc_instancia_mayor.png`

Opción alternativa con ImageMagick:

```bash
import docs/informe/assets/arbol_minizinc_instancia_mayor.png
```

Después de ejecutar ese comando, seleccionar con el mouse la ventana de Gist.

## 4. Actualizar el informe

Después de reemplazar la imagen:

```bash
./docs/scripts/compilar_informe.sh
cp docs/informe/Informe.pdf Informe.pdf
```

Antes de entregar, comprobar que la figura del informe muestre el árbol nuevo
y no una captura anterior al parámetro `maxM`.
