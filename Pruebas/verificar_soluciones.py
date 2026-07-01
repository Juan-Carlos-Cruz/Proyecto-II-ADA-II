#!/usr/bin/env python3
"""Recalcula independientemente costo, balance y polarización."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ProyectoGUIFuentes"))
sys.path.insert(0, str(ROOT / "Pruebas"))

from ejecutar_pruebas import CASES
from pca_parser import read_pca
from result_parser import parse_minizinc_output


def exact(value) -> Fraction:
    """Convierte un valor numérico a una fracción exacta.

    Args:
        value: Valor aceptado por ``Fraction``.

    Returns:
        Fracción equivalente.

    Example:
        >>> exact("0.25")
        Fraction(1, 4)
    """
    return Fraction(value)


def verify(name, pca_path, output_path) -> None:
    """Verifica independientemente una solución guardada.

    Args:
        name: Nombre legible del caso.
        pca_path: Ruta de la entrada PCA.
        output_path: Ruta de la salida original de MiniZinc.

    Returns:
        None. Lanza ``AssertionError`` si una condición falla.

    Example:
        >>> # verify("ejemplo", ruta_pca, ruta_salida)
    """
    instance = read_pca(pca_path)
    result = parse_minizinc_output(output_path.read_text(encoding="utf-8"), instance.m)
    x = result.movements

    assert all(value >= 0 for row in x for value in row)
    assert all(x[i][i] == 0 for i in range(instance.m))
    assert all(sum(x[i]) <= instance.p[i] for i in range(instance.m))

    final = tuple(
        instance.p[i]
        - sum(x[i][j] for j in range(instance.m) if j != i)
        + sum(x[j][i] for j in range(instance.m) if j != i)
        for i in range(instance.m)
    )
    assert final == result.final_distribution
    assert sum(final) == instance.n

    cost = Fraction(0)
    for i in range(instance.m):
        for j in range(instance.m):
            if i == j:
                continue
            unit = exact(instance.c[i][j]) * (
                1 + Fraction(instance.p[i], instance.n)
            )
            if instance.p[j] == 0:
                unit += exact(instance.ce[j])
            cost += unit * x[i][j]
    assert cost == result.total_cost
    assert cost <= exact(instance.ct)

    scores = [
        sum(
            final[i] * abs(exact(instance.v[i]) - exact(instance.v[k]))
            for i in range(instance.m)
        )
        for k in range(instance.m)
    ]
    assert result.polarization == min(scores)
    assert scores[result.median_index - 1] == result.polarization
    assert exact(instance.v[result.median_index - 1]) == result.median_value
    print(f"OK: {name}")


def main() -> None:
    """Verifica las salidas de todos los casos registrados.

    Returns:
        None.

    Example:
        Desde la raíz del proyecto::

            python3 Pruebas/verificar_soluciones.py
    """
    output_directory = ROOT / "Pruebas/salidas_solver"
    for name, pca_path, _, _ in CASES:
        verify(name, pca_path, output_directory / f"{name}.txt")


if __name__ == "__main__":
    main()
