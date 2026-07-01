FUENTES DE LA INTERFAZ MINPOL

app.py
    Punto de entrada mínimo de la aplicación.

ui/main_window.py
    Ventana principal y controlador del flujo cargar → convertir → resolver.

ui/sidebar.py
    Panel lateral, selección del solver y botones de acción.

ui/input_view.py
    Vista de parámetros, opiniones y matriz de costos.

ui/result_view.py
    Vista de movimientos, indicadores y distribución final.

ui/solver_view.py
    Resumen de optimalidad y estadísticas del solver.

ui/components.py
    Tablas, tarjetas, gráfico y contenedor desplazable reutilizables.

ui/dialogs.py
    Ventanas secundarias, incluida la salida técnica de MiniZinc.

ui/theme.py
    Colores y estilos ttk compartidos.

pca_parser.py
    Parser, validaciones y conversión exacta de PCA a DZN.

result_parser.py
    Interpreta la salida etiquetada de Proyecto.mzn.

compliance.py
    Recalcula y comprueba las restricciones de la solución mostrada.

minizinc_runner.py
    Ejecuta MiniZinc mediante subprocess con límite de tiempo.

convertir_pca.py
    Conversor independiente para línea de comandos.

tests/
    Pruebas unitarias del conversor y del parser de resultados.

ARQUITECTURA

    app.py
       └── ui/main_window.py
              ├── ui/sidebar.py
              ├── ui/input_view.py
              ├── ui/result_view.py
              ├── ui/solver_view.py
              ├── ui/components.py
              ├── ui/dialogs.py
              └── ui/theme.py

    Servicios independientes:
       ├── pca_parser.py
       ├── result_parser.py
       ├── compliance.py
       └── minizinc_runner.py

Ejecución:

    python3 ProyectoGUIFuentes/app.py

Conversión sin interfaz:

    python3 ProyectoGUIFuentes/convertir_pca.py entrada.pca salida.dzn

Pruebas:

    python3 -m unittest discover -s ProyectoGUIFuentes/tests -v
