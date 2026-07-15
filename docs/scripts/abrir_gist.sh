#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MINIZINC_BIN="${MINIZINC_EXECUTABLE:-minizinc}"

cd "$ROOT_DIR"
"$MINIZINC_BIN" --solver "Gecode Gist" --statistics \
  Proyecto.mzn DatosProyecto/ejemplos/ejemplo_pdf.dzn
