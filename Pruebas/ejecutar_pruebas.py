#!/usr/bin/env python3
"""Ejecuta de forma reproducible la batería de pruebas del proyecto."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
GUI_SOURCES = ROOT / "ProyectoGUIFuentes"
sys.path.insert(0, str(GUI_SOURCES))

from minizinc_runner import run_minizinc
from mpl_parser import decimal_text, read_mpl, write_dzn
from result_parser import fraction_text, parse_minizinc_output


CASES = [
    (
        "ejemplo_pdf",
        ROOT / "DatosProyecto/ejemplos/ejemplo_pdf.mpl",
        ROOT / "DatosProyecto/ejemplos/ejemplo_pdf.dzn",
        "Instancia de la sección 2.4.",
    ),
    (
        "instancia_01_consenso",
        ROOT / "MisInstancias/instancia_01_consenso.mpl",
        ROOT / "MisInstancias/instancia_01_consenso.dzn",
        "El presupuesto permite alcanzar consenso.",
    ),
    (
        "instancia_02_presupuesto_limitado",
        ROOT / "MisInstancias/instancia_02_presupuesto_limitado.mpl",
        ROOT / "MisInstancias/instancia_02_presupuesto_limitado.dzn",
        "Presupuesto bajo; no se alcanza consenso.",
    ),
    (
        "instancia_03_costos_extra_altos",
        ROOT / "MisInstancias/instancia_03_costos_extra_altos.mpl",
        ROOT / "MisInstancias/instancia_03_costos_extra_altos.dzn",
        "Destinos centrales vacíos con costos extra altos.",
    ),
    (
        "instancia_04_costos_decimales",
        ROOT / "MisInstancias/instancia_04_costos_decimales.mpl",
        ROOT / "MisInstancias/instancia_04_costos_decimales.dzn",
        "Verifica escalamiento exacto de costos decimales.",
    ),
    (
        "instancia_05_grande",
        ROOT / "MisInstancias/instancia_05_grande.mpl",
        ROOT / "MisInstancias/instancia_05_grande.dzn",
        "Mayor número de opiniones y variables.",
    ),
    (
        "ejemplo_ct_00",
        ROOT / "DatosProyecto/experimentos/ejemplo_ct_00.mpl",
        ROOT / "DatosProyecto/experimentos/ejemplo_ct_00.dzn",
        "Control: no se permiten movimientos.",
    ),
    (
        "ejemplo_ct_10",
        ROOT / "DatosProyecto/experimentos/ejemplo_ct_10.mpl",
        ROOT / "DatosProyecto/experimentos/ejemplo_ct_10.dzn",
        "Variación intermedia del presupuesto.",
    ),
    (
        "ejemplo_ct_24",
        ROOT / "DatosProyecto/experimentos/ejemplo_ct_24.mpl",
        ROOT / "DatosProyecto/experimentos/ejemplo_ct_24.dzn",
        "Presupuesto mínimo observado para consenso en opinión 1.",
    ),
    (
        "instancia_03_sin_extra",
        ROOT / "DatosProyecto/experimentos/instancia_03_sin_extra.mpl",
        ROOT / "DatosProyecto/experimentos/instancia_03_sin_extra.dzn",
        "Control de la instancia 03 con ce=0.",
    ),
]


def main() -> int:
    """Ejecuta las instancias y escribe resultados reproducibles.

    Returns:
        Cero cuando toda la batería finaliza correctamente.

    Example:
        Desde la raíz del proyecto::

            python3 Pruebas/ejecutar_pruebas.py
    """
    solver = os.environ.get("MINPOL_SOLVER", "HiGHS")
    output_directory = ROOT / "Pruebas/salidas_solver"
    output_directory.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []

    with TemporaryDirectory(prefix="minpol_pruebas_") as temporary_directory:
        temporary_root = Path(temporary_directory)
        for name, mpl_path, dzn_path, observation in CASES:
            instance = read_mpl(mpl_path)
            generated_dzn = write_dzn(instance, temporary_root / f"{name}.dzn")
            if generated_dzn.read_text(encoding="utf-8") != dzn_path.read_text(
                encoding="utf-8"
            ):
                raise RuntimeError(
                    f"{dzn_path} no coincide con el DZN generado desde {mpl_path}."
                )

            output = run_minizinc(
                ROOT / "Proyecto.mzn",
                generated_dzn,
                solver=solver,
            )
            result = parse_minizinc_output(output, instance.m)
            (output_directory / f"{name}.txt").write_text(output, encoding="utf-8")
            status = (
                "ÓPTIMO"
                if any(line.strip() == "==========" for line in output.splitlines())
                else "FACTIBLE"
            )
            rows.append(
                {
                    "instancia": name,
                    "n": str(instance.n),
                    "m": str(instance.m),
                    "ct": decimal_text(instance.ct),
                    "maxM": str(instance.max_movs),
                    "costo_usado": fraction_text(result.total_cost),
                    "movimientos": str(result.total_movements),
                    "polarizacion": fraction_text(result.polarization),
                    "tiempo_solver_s": result.statistics.get("solveTime", ""),
                    "estado": status,
                    "solver": solver,
                    "nodos": result.statistics.get("nodes", ""),
                    "observaciones": observation,
                }
            )

            if mpl_path.parent == ROOT / "MisInstancias":
                result_lines = [
                    f"Instancia: {name}",
                    f"Estado: {status}",
                    f"Solver: {solver}",
                    f"Distribución final: {list(result.final_distribution)}",
                    f"Costo usado: {fraction_text(result.total_cost)}",
                    f"Movimientos usados: {result.total_movements}",
                    f"Máximo de movimientos: {instance.max_movs}",
                    f"Polarización óptima: {fraction_text(result.polarization)}",
                    f"Índice de mediana: {result.median_index}",
                    f"Valor de mediana: {fraction_text(result.median_value)}",
                    "Matriz de movimientos:",
                    *[",".join(map(str, row)) for row in result.movements],
                    "",
                ]
                (ROOT / "MisInstancias" / f"{name}.resultado.txt").write_text(
                    "\n".join(result_lines),
                    encoding="utf-8",
                )

    csv_path = ROOT / "Pruebas/resultados.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    mirror_path = ROOT / "DatosProyecto/resultados/resultados_pruebas.csv"
    mirror_path.write_bytes(csv_path.read_bytes())
    print(f"Se ejecutaron {len(rows)} pruebas con {solver}.")
    print(f"Tabla: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
