# Presentación de sustentación

Archivos:

- `Presentacion_MinPol.tex`: fuente principal profesional en LaTeX Beamer.
- `Presentacion_MinPol.pdf`: versión compilada desde la fuente Beamer.
- `Presentacion_MinPol.pptx`: versión editable para PowerPoint o LibreOffice.
- `Presentacion_MinPol.odp`: fuente editable nativa de LibreOffice Impress.
- `generar_presentacion.py`: generador reproducible de ODP y PPTX; no
  sobrescribe el PDF compilado desde LaTeX.
- `GUIA_USO.md`: orden de diapositivas, tiempos y acciones de la demostración.

El texto hablado completo se encuentra en `../video/GuionVideo.md`.

## Regeneración

La versión PDF principal se compila desde la raíz del repositorio con:

```bash
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=docs/presentacion \
  docs/presentacion/Presentacion_MinPol.tex
```

Ejecutar el comando dos veces actualiza correctamente las referencias.

### Formatos de oficina

El generador se conecta a una instancia local de LibreOffice mediante una
tubería UNO. Desde la raíz del repositorio:

```bash
soffice --headless --accept='pipe,name=minpol_presentacion;urp;' \
  --norestore --nodefault --nofirststartwizard \
  -env:UserInstallation=file:///tmp/minpol_lo_profile &

python3 docs/presentacion/generar_presentacion.py
```

Las imágenes usadas provienen de `docs/informe/assets` y quedan incrustadas
en los archivos de presentación.
