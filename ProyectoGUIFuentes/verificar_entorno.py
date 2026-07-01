#!/usr/bin/env python3
"""Comprueba las dependencias necesarias para ejecutar MinPol."""

from __future__ import annotations

import platform
import subprocess
import sys

from minizinc_runner import MiniZincRunError, find_minizinc


def check_python() -> tuple[bool, str]:
    """Comprueba que la versión activa de Python sea compatible.

    Returns:
        Tupla con el estado y una descripción de la versión encontrada.

    Example:
        >>> check_python()[0] == (sys.version_info >= (3, 10))
        True
    """

    compatible = sys.version_info >= (3, 10)
    version = platform.python_version()
    return compatible, f"Python {version}"


def check_tkinter() -> tuple[bool, str]:
    """Comprueba que Tkinter pueda importarse sin abrir una ventana.

    Returns:
        Tupla con el estado y la versión de Tcl/Tk, si está disponible.

    Example:
        >>> estado, detalle = check_tkinter()
        >>> isinstance(estado, bool) and bool(detalle)
        True
    """

    try:
        import tkinter
    except ImportError as exc:
        return False, f"Tkinter no disponible: {exc}"
    return True, f"Tkinter con Tcl/Tk {tkinter.TclVersion}"


def check_minizinc() -> tuple[bool, str]:
    """Localiza MiniZinc y consulta su versión mediante la línea de comandos.

    Returns:
        Tupla con el estado y la primera línea informativa de MiniZinc.

    Example:
        >>> estado, detalle = check_minizinc()
        >>> isinstance(estado, bool) and bool(detalle)
        True
    """

    try:
        executable = find_minizinc()
    except MiniZincRunError as exc:
        return False, str(exc)
    try:
        completed = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"No fue posible consultar MiniZinc: {exc}"
    output = (completed.stdout or completed.stderr).strip().splitlines()
    detail = output[0] if output else executable
    return completed.returncode == 0, detail


def check_solvers() -> tuple[bool, str]:
    """Comprueba que exista al menos un solver soportado por la interfaz.

    Returns:
        Tupla con el estado y los solvers compatibles encontrados.

    Example:
        >>> estado, detalle = check_solvers()
        >>> isinstance(estado, bool) and bool(detalle)
        True
    """

    try:
        executable = find_minizinc()
        completed = subprocess.run(
            [executable, "--solvers"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
    except (MiniZincRunError, OSError, subprocess.TimeoutExpired) as exc:
        return False, f"No fue posible consultar los solvers: {exc}"

    supported = [
        name
        for name in ("Chuffed", "HiGHS", "COIN-BC")
        if name.casefold() in completed.stdout.casefold()
    ]
    if not supported:
        return False, "No se encontró Chuffed, HiGHS ni COIN-BC."
    return True, "Solvers disponibles: " + ", ".join(supported)


def main() -> int:
    """Ejecuta todas las comprobaciones y devuelve un código apto para CI.

    Returns:
        Cero cuando el entorno es compatible; uno si falta un requisito.

    Example:
        Desde la raíz del proyecto::

            python3 ProyectoGUIFuentes/verificar_entorno.py
    """

    checks = (
        ("Python", check_python),
        ("Tkinter", check_tkinter),
        ("MiniZinc", check_minizinc),
        ("Solvers", check_solvers),
    )
    all_ok = True
    print(f"Sistema: {platform.system()} {platform.release()}")
    for name, check in checks:
        passed, detail = check()
        all_ok &= passed
        print(f"[{'OK' if passed else 'ERROR'}] {name}: {detail}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
