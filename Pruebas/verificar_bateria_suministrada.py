#!/usr/bin/env python3
"""Valida y resuelve las instancias incluidas en ``bateria_pruebas/mpl``."""

from __future__ import annotations

import csv
import os
import sys
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent.parent
GUI_SOURCES = ROOT / "ProyectoGUIFuentes"
sys.path.insert(0, str(GUI_SOURCES))

from compliance import evaluate_compliance
from minizinc_runner import run_minizinc
from mpl_parser import decimal_text, read_mpl, write_dzn
from result_parser import fraction_text, parse_minizinc_output


REFERENCE_VALUES = dict(
    zip(
        (f"MinPol{number}.mpl" for number in range(1, 31)),
        (
            "0.09", "0", "0", "0", "0.482", "0.003", "3.085", "4.323",
            "5.373", "9.686", "10.349", "3.721", "12.417", "6.549",
            "10.313", "18.786", "14.171", "17.897", "19.603", "23.566",
            "24.175", "31.135", "3.822", "29.902", "24.775", "30.748",
            "25.021", "14.683", "29.999", "0",
        ),
        strict=True,
    )
)
REFERENCE_TOLERANCE = Fraction(1, 1000)


def _instance_number(path: Path) -> int:
    """Extrae el número de un nombre de la forma ``MinPolN.mpl``."""

    return int(path.stem.removeprefix("MinPol"))


def main() -> int:
    """Genera un CSV reproducible con resultados y errores de entrada."""

    source_directory = ROOT / "bateria_pruebas/mpl"
    paths = sorted(source_directory.glob("MinPol*.mpl"), key=_instance_number)
    expected_names = {f"MinPol{number}.mpl" for number in range(1, 31)}
    actual_names = {path.name for path in paths}
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        unexpected = sorted(actual_names - expected_names)
        raise RuntimeError(
            f"Batería incompleta. Faltan: {missing}; inesperadas: {unexpected}."
        )

    # COIN-BC reproduce el óptimo de referencia de MinPol15. HiGHS 1.14.0
    # reportó 10.342 en esa instancia, mientras COIN-BC, Gecode y Chuffed
    # certificaron el valor de referencia 10.313.
    solver = os.environ.get("MINPOL_SOLVER", "COIN-BC")
    rows: list[dict[str, str]] = []
    optimal_count = 0

    with TemporaryDirectory(prefix="minpol_bateria_") as temporary_directory:
        temporary_root = Path(temporary_directory)
        for path in paths:
            base_row = {
                "instancia": path.name,
                "n": "",
                "m": "",
                "ct": "",
                "maxM": "",
                "costo_usado": "",
                "movimientos": "",
                "polarizacion": "",
                "valor_profesor": REFERENCE_VALUES[path.name],
                "diferencia_profesor": "",
                "tiempo_solver_s": "",
                "nodos": "",
                "solver": solver,
                "estado": "",
                "detalle": "",
            }
            instance = read_mpl(path)

            generated_dzn = write_dzn(
                instance,
                temporary_root / f"{path.stem}.dzn",
            )
            output = run_minizinc(
                ROOT / "Proyecto.mzn",
                generated_dzn,
                solver=solver,
            )
            result = parse_minizinc_output(output, instance.m)
            checks = evaluate_compliance(instance, result)
            failed_checks = [check.name for check in checks if not check.passed]
            if failed_checks:
                raise RuntimeError(
                    f"{path.name} incumple: {', '.join(failed_checks)}."
                )

            reference = Fraction(REFERENCE_VALUES[path.name])
            reference_difference = abs(result.polarization - reference)
            if reference_difference > REFERENCE_TOLERANCE:
                raise RuntimeError(
                    f"{path.name} obtuvo {fraction_text(result.polarization)}, "
                    f"pero la referencia es {REFERENCE_VALUES[path.name]}."
                )

            optimal = any(
                line.strip() == "==========" for line in output.splitlines()
            )
            base_row.update(
                {
                    "n": str(instance.n),
                    "m": str(instance.m),
                    "ct": decimal_text(instance.ct),
                    "maxM": str(instance.max_movs),
                    "costo_usado": fraction_text(result.total_cost),
                    "movimientos": str(result.total_movements),
                    "polarizacion": fraction_text(result.polarization),
                    "diferencia_profesor": fraction_text(reference_difference),
                    "tiempo_solver_s": result.statistics.get("solveTime", ""),
                    "nodos": result.statistics.get("nodes", ""),
                    "estado": "ÓPTIMO" if optimal else "FACTIBLE",
                    "detalle": (
                        "Comprobaciones independientes aprobadas y diferencia "
                        "con el profesor no mayor que 0.001."
                    ),
                }
            )
            rows.append(base_row)
            optimal_count += int(optimal)

    destination = ROOT / "Pruebas/resultados_bateria_suministrada.csv"
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Batería suministrada: {optimal_count} óptimas de {len(rows)} archivos."
    )
    print(f"Tabla: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
