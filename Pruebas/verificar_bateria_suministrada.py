#!/usr/bin/env python3
"""Valida y resuelve las instancias incluidas en ``bateria_pruebas/mpl``."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent.parent
GUI_SOURCES = ROOT / "ProyectoGUIFuentes"
sys.path.insert(0, str(GUI_SOURCES))

from compliance import evaluate_compliance
from minizinc_runner import run_minizinc
from mpl_parser import MPLValidationError, decimal_text, read_mpl, write_dzn
from result_parser import fraction_text, parse_minizinc_output


EXPECTED_INVALID = {
    "MinPol28.mpl": "la suma de p es 125, pero n es 100",
    "MinPol29.mpl": "la suma de p es 125, pero n es 100",
}


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

    solver = os.environ.get("MINPOL_SOLVER", "HiGHS")
    rows: list[dict[str, str]] = []
    optimal_count = 0
    invalid_count = 0

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
                "tiempo_solver_s": "",
                "nodos": "",
                "solver": solver,
                "estado": "",
                "detalle": "",
            }
            try:
                instance = read_mpl(path)
            except MPLValidationError as exc:
                expected_message = EXPECTED_INVALID.get(path.name)
                if expected_message is None or expected_message not in str(exc):
                    raise
                base_row["estado"] = "ENTRADA INVÁLIDA ESPERADA"
                base_row["detalle"] = str(exc)
                rows.append(base_row)
                invalid_count += 1
                continue
            if path.name in EXPECTED_INVALID:
                raise RuntimeError(
                    f"{path.name} dejó de presentar la inconsistencia esperada."
                )

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
                    "tiempo_solver_s": result.statistics.get("solveTime", ""),
                    "nodos": result.statistics.get("nodes", ""),
                    "estado": "ÓPTIMO" if optimal else "FACTIBLE",
                    "detalle": "Todas las comprobaciones independientes pasaron.",
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
        f"Batería suministrada: {optimal_count} óptimas, "
        f"{invalid_count} entradas inválidas, {len(rows)} archivos."
    )
    print(f"Tabla: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
