#!/usr/bin/env python3
"""Conversor de línea de comandos: archivo.pca -> archivo.dzn."""

from __future__ import annotations

import argparse
import sys

from pca_parser import PCAValidationError, convert_pca_to_dzn


def main() -> int:
    """Procesa argumentos y ejecuta la conversión PCA a DZN.

    Returns:
        Cero si se generó el archivo y dos si la entrada no es válida.

    Example:
        Desde la raíz del proyecto::

            python3 ProyectoGUIFuentes/convertir_pca.py entrada.pca salida.dzn
    """
    parser = argparse.ArgumentParser(
        description="Valida una instancia MinPol .pca y genera su archivo .dzn."
    )
    parser.add_argument("entrada", help="Ruta del archivo .pca")
    parser.add_argument(
        "salida",
        nargs="?",
        default="DatosProyecto.dzn",
        help="Ruta de salida (por defecto: DatosProyecto.dzn)",
    )
    arguments = parser.parse_args()
    try:
        destination = convert_pca_to_dzn(arguments.entrada, arguments.salida)
    except PCAValidationError as exc:
        print(f"Error de validación: {exc}", file=sys.stderr)
        return 2
    print(f"Archivo generado: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
