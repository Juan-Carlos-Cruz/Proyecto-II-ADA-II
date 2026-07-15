"""Interpretación de la salida etiquetada producida por Proyecto.mzn."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from fractions import Fraction


class ResultParseError(ValueError):
    """Indica que la salida de MiniZinc no tiene el formato esperado."""

    pass


@dataclass(frozen=True)
class MinPolResult:
    movements: tuple[tuple[int, ...], ...]
    final_distribution: tuple[int, ...]
    total_cost: Fraction
    total_movements: int
    polarization: Fraction
    median_index: int
    median_value: Fraction
    statistics: dict[str, str] = field(default_factory=dict)
    raw_output: str = ""


def _fraction(values: dict[str, str], name: str) -> Fraction:
    """Extrae una fracción etiquetada de la salida de MiniZinc.

    Args:
        values: Pares de etiqueta y valor analizados.
        name: Etiqueta requerida.

    Returns:
        Fracción exacta correspondiente.

    Example:
        >>> _fraction({"COSTO": "3/2"}, "COSTO")
        Fraction(3, 2)
    """
    try:
        return Fraction(values[name])
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        raise ResultParseError(f"No se encontró un valor válido para {name}.") from exc


def parse_minizinc_output(output: str, m: int) -> MinPolResult:
    """Interpreta la salida estable producida por ``Proyecto.mzn``.

    Args:
        output: Salida estándar completa de MiniZinc.
        m: Número esperado de opiniones.

    Returns:
        Resultado estructurado con solución, estadísticas y salida original.

    Example:
        >>> # resultado = parse_minizinc_output(salida, m=5)
    """
    if "=====UNSATISFIABLE=====" in output:
        raise ResultParseError("La instancia no tiene solución factible.")
    if "=====UNKNOWN=====" in output:
        raise ResultParseError("El solver no pudo determinar una solución.")
    if "MATRIZ_MOVIMIENTOS" not in output:
        raise ResultParseError("La salida no contiene la matriz de movimientos.")

    lines = output.splitlines()
    marker = lines.index("MATRIZ_MOVIMIENTOS")
    if len(lines) < marker + 1 + m:
        raise ResultParseError("La matriz de movimientos está incompleta.")

    rows: list[tuple[int, ...]] = []
    for row_number, line in enumerate(lines[marker + 1 : marker + 1 + m], start=1):
        try:
            row = tuple(int(value.strip()) for value in line.split(","))
        except ValueError as exc:
            raise ResultParseError(
                f"La fila {row_number} de movimientos no es válida."
            ) from exc
        if len(row) != m:
            raise ResultParseError(
                f"La fila {row_number} debe contener {m} movimientos."
            )
        rows.append(row)

    values: dict[str, str] = {}
    for line in lines[marker + 1 + m :]:
        if "=" in line and not line.startswith("%%%"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

    try:
        distribution_object = ast.literal_eval(values["DISTRIBUCION_FINAL"])
        distribution = tuple(int(value) for value in distribution_object)
    except (KeyError, ValueError, SyntaxError, TypeError) as exc:
        raise ResultParseError("La distribución final no es válida.") from exc
    if len(distribution) != m:
        raise ResultParseError(f"La distribución final debe contener {m} valores.")

    statistics: dict[str, str] = {}
    pattern = re.compile(r"^%%%mzn-stat:\s*([^=]+)=(.*)$")
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            statistics[match.group(1).strip()] = match.group(2).strip().strip('"')

    try:
        median_index = int(values["INDICE_MEDIANA"])
    except (KeyError, ValueError) as exc:
        raise ResultParseError("El índice de la mediana no es válido.") from exc

    try:
        total_movements = int(values["TOTAL_MOVIMIENTOS"])
    except (KeyError, ValueError) as exc:
        raise ResultParseError("El total de movimientos no es válido.") from exc

    return MinPolResult(
        movements=tuple(rows),
        final_distribution=distribution,
        total_cost=_fraction(values, "COSTO_TOTAL"),
        total_movements=total_movements,
        polarization=_fraction(values, "POLARIZACION"),
        median_index=median_index,
        median_value=_fraction(values, "VALOR_MEDIANA"),
        statistics=statistics,
        raw_output=output,
    )


def fraction_text(value: Fraction) -> str:
    """Presenta una fracción como entero o decimal acompañado del valor exacto.

    Args:
        value: Fracción que se desea mostrar.

    Returns:
        Texto legible para la interfaz.

    Example:
        >>> fraction_text(Fraction(3, 2))
        '1.5 (3/2)'
    """
    if value.denominator == 1:
        return str(value.numerator)
    decimal = value.numerator / value.denominator
    return f"{decimal:.10g} ({value.numerator}/{value.denominator})"
