#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="$ROOT_DIR/docs/.build"
cd "$ROOT_DIR"
mkdir -p "$BUILD_DIR"

pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory="$BUILD_DIR" docs/informe/Informe.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory="$BUILD_DIR" docs/informe/Informe.tex

cp "$BUILD_DIR/Informe.pdf" "$ROOT_DIR/docs/informe/Informe.pdf"

echo "Informe generado en: $ROOT_DIR/docs/informe/Informe.pdf"
