# Documentación del proyecto

La documentación está separada por propósito:

- `informe/`: fuente LaTeX, PDF compilado y recursos gráficos.
- `analisis/`: modelo matemático y análisis experimental.
- `video/`: guion del video explicativo.
- `entrega/`: lista de pendientes antes de entregar.
- `scripts/`: herramientas para construir la documentación.
- `.build/`: archivos auxiliares generados por LaTeX.

## Compilar el informe

Desde la raíz del proyecto:

```bash
./docs/scripts/compilar_informe.sh
```

El script genera `docs/informe/Informe.pdf` y mantiene los archivos auxiliares de
LaTeX dentro de `docs/.build/`, que está ignorado por Git.

Para construir el ZIP exigido por el enunciado, el PDF debe copiarse como
`Informe.pdf` en la raíz temporal del paquete. El archivo fuente permanece
organizado en `docs/`.
