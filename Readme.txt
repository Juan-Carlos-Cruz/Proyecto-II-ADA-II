PROYECTO MINPOL — ANÁLISIS DE ALGORITMOS II
===========================================

Este proyecto resuelve el problema de minimizar la polarización de una
población mediante programación lineal entera. A partir de una instancia
*.pca, la aplicación valida los datos, genera DatosProyecto.dzn, ejecuta el
modelo genérico Proyecto.mzn y muestra la solución y el cumplimiento de sus
restricciones.

1. INICIO RÁPIDO
----------------

Requisitos:

- Python 3.10 o posterior.
- Tkinter, incluido normalmente con Python en Windows y macOS.
- MiniZinc 2.9.7 recomendado, con Chuffed, HiGHS o COIN-BC.
- Pillow sólo si se desean regenerar los gráficos del informe.

Comprobar el entorno desde la raíz del proyecto:

    python3 ProyectoGUIFuentes/verificar_entorno.py

En Windows también puede utilizarse "py" en lugar de "python3".

Ejecutar la interfaz:

    python3 ProyectoGUIFuentes/app.py

Flujo de uso:

1. Presionar "Cargar archivo .pca".
2. Seleccionar una instancia, por ejemplo:
   DatosProyecto/ejemplos/ejemplo_pdf.pca.
3. Revisar los parámetros y la matriz de costos.
4. Seleccionar un solver.
5. Presionar "Resolver instancia".
6. Revisar la solución, las seis comprobaciones de restricciones y las
   estadísticas del solver.

La aplicación crea DatosProyecto.dzn en la raíz, ejecuta Proyecto.mzn y
muestra matriz de movimientos, distribución final, costo, polarización,
mediana y certificado de optimalidad.

2. INSTALACIÓN POR SISTEMA OPERATIVO
------------------------------------

Windows:

1. Instalar Python y activar la opción para agregarlo al PATH.
2. Instalar MiniZinc y comprobar en PowerShell:

       py --version
       minizinc --version
       py ProyectoGUIFuentes\verificar_entorno.py
       py ProyectoGUIFuentes\app.py

Si MiniZinc no está en PATH:

    $env:MINIZINC_EXECUTABLE="C:\ruta\MiniZinc\minizinc.exe"

macOS:

1. Instalar Python 3 con soporte Tk y MiniZinc.
2. Comprobar y ejecutar:

       python3 --version
       minizinc --version
       python3 ProyectoGUIFuentes/verificar_entorno.py
       python3 ProyectoGUIFuentes/app.py

Linux (Debian/Ubuntu):

1. Instalar Python, Tkinter y MiniZinc mediante el gestor de paquetes o el
   instalador oficial correspondiente.
2. Comprobar y ejecutar:

       python3 --version
       minizinc --version
       python3 ProyectoGUIFuentes/verificar_entorno.py
       python3 ProyectoGUIFuentes/app.py

En Linux, si falta Tkinter, el paquete suele llamarse "python3-tk".

En cualquier sistema puede indicarse manualmente el ejecutable:

    MINIZINC_EXECUTABLE=/ruta/al/bin/minizinc

3. MODELO DEL PROBLEMA
----------------------

Parámetros principales:

- n: número total de personas.
- m: número de opiniones.
- p[i]: personas inicialmente en la opinión i.
- v[i]: valor numérico de la opinión i.
- c[i,j]: costo base de mover una persona de i a j.
- ce[j]: costo extra si la opinión j estaba inicialmente vacía.
- ct: presupuesto máximo.

La variable entera x[i,j] indica cuántas personas pasan de la opinión i a la
j. La variable y[i] representa la población final. El modelo:

- prohíbe automovimientos;
- limita las salidas por la población inicial de cada opinión;
- conserva la población mediante ecuaciones de balance;
- impone que el costo total no supere ct;
- selecciona una mediana ponderada mediante variables binarias;
- minimiza la suma de distancias absolutas a esa mediana.

Los decimales se convierten exactamente a enteros escalados. De esta forma,
Proyecto.mzn sigue siendo un modelo lineal entero y no depende de errores de
punto flotante. La formulación completa y su justificación están en:

    docs/informe/Informe.pdf
    docs/analisis/ModeloMatematico.md

4. FORMATO DE ENTRADA PCA
-------------------------

Línea 1: n.
Línea 2: m.
Línea 3: p, con m enteros separados por comas.
Línea 4: v, con m valores separados por comas.
Línea 5: ce, con m valores separados por comas.
Línea 6: ct.
Siguientes m líneas: matriz c de m por m.

Los decimales deben usar punto. Las líneas vacías se ignoran.

La representación del ejemplo impreso en el enunciado omite aparentemente
la línea "5" correspondiente a m. La sección 3.1 sí exige esa línea, por lo
que DatosProyecto/ejemplos/ejemplo_pdf.pca la incluye.

5. USO SIN INTERFAZ
-------------------

Convertir una instancia:

    python3 ProyectoGUIFuentes/convertir_pca.py \
        DatosProyecto/ejemplos/ejemplo_pdf.pca DatosProyecto.dzn

Ejecutar MiniZinc directamente:

    minizinc --solver HiGHS --statistics \
        Proyecto.mzn DatosProyecto.dzn

Para el ejemplo se espera una solución óptima con distribución
[18,2,0,0,0], costo 19.2 y polarización 0.5.

6. PRUEBAS Y REPRODUCIBILIDAD
-----------------------------

Pruebas unitarias:

    python3 -m unittest discover -s ProyectoGUIFuentes/tests -v

Batería de diez instancias:

    python3 Pruebas/ejecutar_pruebas.py

Verificación independiente de restricciones y objetivo:

    python3 Pruebas/verificar_soluciones.py

Regenerar gráficos (requiere Pillow):

    python3 -m pip install -r requirements-dev.txt
    python3 Pruebas/generar_graficos.py

Compilar el informe (requiere pdflatex):

    ./docs/scripts/compilar_informe.sh

7. ESTRUCTURA DE ARCHIVOS
-------------------------

Proyecto.mzn
    Modelo genérico de programación lineal entera solicitado.

DatosProyecto.dzn
    Archivo generado por la interfaz; no debe editarse manualmente.

DatosProyecto/
    Ejemplo del enunciado, experimentos, caso de Branch and Bound y resultados.

MisInstancias/
    Cinco instancias del grupo. Cada una incluye PCA, DZN y solución esperada.

ProyectoGUIFuentes/
    Código fuente de la interfaz, validadores, conversores y pruebas unitarias.

ProyectoGUIFuentes/ui/
    Vistas y componentes Tkinter.

Pruebas/
    Ejecución reproducible, verificación independiente, CSV y salidas técnicas.

docs/informe/
    Fuente LaTeX, PDF compilado y recursos gráficos.

docs/analisis/
    Desarrollo matemático y análisis experimental complementario.

docs/entrega/
    Auditoría de rúbrica y lista de pendientes antes de entregar.

docs/video/
    Guion para el video explicativo.

8. ARQUITECTURA
---------------

    archivo PCA
        |
        v
    pca_parser.py ----> DatosProyecto.dzn
        |                       |
        |                       v
        +--------------> Proyecto.mzn + MiniZinc
                                   |
                                   v
    interfaz <---- result_parser.py + compliance.py

pca_parser.py valida el formato y escala decimales. minizinc_runner.py ejecuta
el proceso con límite de tiempo. result_parser.py interpreta la salida.
compliance.py recalcula costo, balance, presupuesto, mediana y objetivo sin
confiar únicamente en las etiquetas del solver.

9. PORTABILIDAD Y DOCKER
------------------------

La ejecución nativa es la opción principal para la interfaz. Tkinter utiliza
el servidor gráfico y los diálogos de archivos del sistema anfitrión; Docker
no los expone de forma uniforme entre Linux, Windows y macOS. Un contenedor
requeriría configuraciones distintas de X11, Wayland o un escritorio remoto,
lo que haría la demostración más difícil, no más sencilla.

Docker sí sería útil para automatizar únicamente el solver y las pruebas en
integración continua. No se adopta como método principal porque la entrega
evalúa una interfaz gráfica de escritorio. El script verificar_entorno.py y
las instrucciones por sistema ofrecen una ruta más directa y verificable.

10. SOLUCIÓN DE PROBLEMAS
-------------------------

"No se encontró minizinc":
    Agregar MiniZinc al PATH o definir MINIZINC_EXECUTABLE.

"No module named tkinter":
    Instalar el componente Tk de la distribución de Python.

"No existe un solver":
    Ejecutar "minizinc --solvers" y seleccionar en la interfaz uno instalado.

"Archivo PCA inválido":
    Revisar el número de líneas, las dimensiones, suma(p)=n, v en [0,1] y
    costos no negativos.

11. ENTREGA
-----------

Antes de comprimir el proyecto debe revisarse:

    docs/entrega/CHECKLIST_ENTREGA.md
    docs/entrega/AUDITORIA_RUBRICA.md

El ZIP final debe conservar los nombres exigidos por el enunciado:
Readme.txt, Informe.pdf, Proyecto.mzn, DatosProyecto/, ProyectoGUIFuentes/ y
MisInstancias/.
