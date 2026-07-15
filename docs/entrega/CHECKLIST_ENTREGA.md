# Checklist de entrega

## Informe y rúbrica

- [x] Reemplazar nombres y códigos de los integrantes.
- [ ] Reemplazar la captura de Gecode Gist por una generada con el modelo
  actualizado `.mpl` + `maxM`.
- [x] Verificar que modelo matemático y `Proyecto.mzn` coincidan.
- [x] Actualizar la tabla si se repiten las pruebas.
- [x] Confirmar formato `.mpl`, orden actualizado y restricción `maxM`.
- [ ] Añadir el enlace verificable del video.
- [x] Compilar el PDF sin errores.

## Video

- [ ] Duración máxima de 15 minutos.
- [ ] Participan todos los integrantes.
- [ ] Explica parámetros, variables, restricciones, objetivo y tipo de modelo,
  incluido `maxM`.
- [x] El informe explica Branch and Bound con cotas, incumbente y poda.
- [ ] Muestra al menos dos configuraciones.
- [ ] Muestra la generación de `DatosProyecto.dzn`.
- [ ] Muestra solución y las siete comprobaciones de restricciones.
- [ ] El enlace abre sin solicitar permisos.

## Ejecución

- [x] Ejecutar `python3 ProyectoGUIFuentes/verificar_entorno.py`.
- [x] Ejecutar las ocho pruebas unitarias.
- [x] Ejecutar la batería de diez instancias.
- [x] Ejecutar la verificación independiente.
- [x] Procesar las 30 entradas suministradas: 28 óptimas y dos rechazadas
  por inconsistencia entre `n` y la suma de `p`.
- [ ] Probar la interfaz desde una copia limpia.
- [ ] Probar otro sistema operativo o declarar cuál se probó realmente.

## ZIP

- [ ] `Readme.txt`.
- [x] `Informe.pdf` en la raíz.
- [ ] `Proyecto.mzn`.
- [ ] `DatosProyecto/`.
- [ ] `ProyectoGUIFuentes/`.
- [ ] `MisInstancias/`.
- [ ] Nombre exigido con los códigos estudiantiles.
- [ ] Excluir `.build/`, `__pycache__/`, temporales y entornos virtuales.
