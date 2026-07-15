"""Comprobación independiente de las restricciones sobre una solución."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from mpl_parser import MinPolInstance
from result_parser import MinPolResult, fraction_text


@dataclass(frozen=True)
class ComplianceCheck:
    name: str
    detail: str
    passed: bool


def _fraction(value: Decimal) -> Fraction:
    """Convierte un decimal exacto a fracción.

    Args:
        value: Decimal que se desea convertir.

    Returns:
        Fracción equivalente sin pérdida.

    Example:
        >>> _fraction(Decimal("0.25"))
        Fraction(1, 4)
    """
    return Fraction(value)


def evaluate_compliance(
    instance: MinPolInstance,
    result: MinPolResult,
) -> tuple[ComplianceCheck, ...]:
    """Recalcula las restricciones sin confiar en el solver.

    Args:
        instance: Datos originales validados.
        result: Solución interpretada desde MiniZinc.

    Returns:
        Comprobaciones independientes de factibilidad y objetivo.

    Example:
        >>> # checks = evaluate_compliance(instancia, resultado)
        >>> # all(check.passed for check in checks)
    """

    movements = result.movements
    final = result.final_distribution
    m = instance.m

    dimensions_ok = (
        len(movements) == m
        and all(len(row) == m for row in movements)
        and len(final) == m
    )
    nonnegative = dimensions_ok and all(
        isinstance(value, int) and value >= 0
        for row in movements
        for value in row
    ) and all(isinstance(value, int) and value >= 0 for value in final)
    diagonal_ok = dimensions_ok and all(movements[i][i] == 0 for i in range(m))

    departures_ok = dimensions_ok and all(
        sum(movements[i][j] for j in range(m) if j != i) <= instance.p[i]
        for i in range(m)
    )
    balance_ok = dimensions_ok and all(
        final[i]
        == instance.p[i]
        - sum(movements[i][j] for j in range(m) if j != i)
        + sum(movements[j][i] for j in range(m) if j != i)
        for i in range(m)
    )
    population_ok = dimensions_ok and sum(final) == instance.n

    expected_cost = Fraction(0)
    if dimensions_ok:
        for i in range(m):
            origin_factor = Fraction(instance.n + instance.p[i], instance.n)
            for j in range(m):
                if i == j:
                    continue
                unit_cost = _fraction(instance.c[i][j]) * origin_factor
                if instance.p[j] == 0:
                    unit_cost += _fraction(instance.ce[j])
                expected_cost += movements[i][j] * unit_cost
    budget = _fraction(instance.ct)
    cost_ok = dimensions_ok and expected_cost == result.total_cost
    budget_ok = cost_ok and expected_cost <= budget

    expected_movements = 0
    if dimensions_ok:
        expected_movements = sum(
            abs(j - i) * movements[i][j]
            for i in range(m)
            for j in range(m)
            if i != j
        )
    movements_ok = (
        dimensions_ok
        and expected_movements == result.total_movements
        and expected_movements <= instance.max_movs
    )

    expected_polarization = Fraction(0)
    median_optimal = False
    if dimensions_ok and 1 <= result.median_index <= m:
        median_value_matches = (
            result.median_value == _fraction(instance.v[result.median_index - 1])
        )
        expected_polarization = sum(
            (
                final[i]
                * abs(_fraction(instance.v[i]) - result.median_value)
                for i in range(m)
            ),
            Fraction(0),
        )
        candidate_scores = [
            sum(
                (
                    final[i]
                    * abs(_fraction(instance.v[i]) - _fraction(instance.v[k]))
                    for i in range(m)
                ),
                Fraction(0),
            )
            for k in range(m)
        ]
        median_optimal = (
            median_value_matches
            and expected_polarization == min(candidate_scores)
            and expected_polarization == result.polarization
        )

    return (
        ComplianceCheck(
            "Dominio entero",
            "Movimientos y población no negativos",
            nonnegative,
        ),
        ComplianceCheck(
            "Sin automovimientos",
            "x[i,i] = 0 para toda opinión",
            diagonal_ok,
        ),
        ComplianceCheck(
            "Disponibilidad",
            "Salidas no exceden la población inicial",
            departures_ok,
        ),
        ComplianceCheck(
            "Balance poblacional",
            f"{sum(final) if dimensions_ok else '—'} = n={instance.n}",
            balance_ok and population_ok,
        ),
        ComplianceCheck(
            "Presupuesto",
            f"{fraction_text(expected_cost)} ≤ {fraction_text(budget)}",
            budget_ok,
        ),
        ComplianceCheck(
            "Límite de movimientos",
            f"{expected_movements} ≤ {instance.max_movs}",
            movements_ok,
        ),
        ComplianceCheck(
            "Mediana y objetivo",
            f"Polarización recalculada: {fraction_text(expected_polarization)}",
            median_optimal,
        ),
    )
