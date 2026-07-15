#!/usr/bin/env python3
"""Conversor de línea de comandos: archivo.mpl -> archivo.dzn."""

from __future__ import annotations

import argparse
import sys

from mpl_parser import MPLValidationError, convert_mpl_to_dzn


def main() -> int:
    """Procesa argumentos y ejecuta la conversión MPL a DZN.

    Returns:
        Cero si se generó el archivo y dos si la entrada no es válida.

    Example:
        Desde la raíz del proyecto::

            python3 ProyectoGUIFuentes/convertir_mpl.py entrada.mpl salida.dzn
    """
    parser = argparse.ArgumentParser(
        description="Valida una instancia MinPol .mpl y genera su archivo .dzn."
    )
    parser.add_argument("entrada", help="Ruta del archivo .mpl")
    parser.add_argument(
        "salida",
        nargs="?",
        default="DatosProyecto.dzn",
        help="Ruta de salida (por defecto: DatosProyecto.dzn)",
    )
    arguments = parser.parse_args()
    try:
        destination = convert_mpl_to_dzn(arguments.entrada, arguments.salida)
    except MPLValidationError as exc:
        print(f"Error de validación: {exc}", file=sys.stderr)
        return 2
    print(f"Archivo generado: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
