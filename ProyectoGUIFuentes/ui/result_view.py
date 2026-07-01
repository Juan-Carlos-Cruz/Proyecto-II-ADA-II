"""Vista de solución, movimientos y distribución final."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from compliance import evaluate_compliance
from pca_parser import MinPolInstance
from result_parser import MinPolResult, fraction_text

from .components import (
    DistributionChart,
    MatrixTable,
    clear_tree,
    metric_card,
    tree_with_scrollbars,
)


class ResultView(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        """Construye la vista de solución y cumplimiento.

        Args:
            parent: Contenedor Tkinter propietario.

        Returns:
            None.

        Example:
            >>> # vista = ResultView(notebook)
        """
        super().__init__(parent, style="Surface.TFrame", padding=16)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.values = {
            "polarization": tk.StringVar(value="—"),
            "cost": tk.StringVar(value="—"),
            "median": tk.StringVar(value="—"),
            "time": tk.StringVar(value="—"),
        }

        cards = ttk.Frame(self, style="Surface.TFrame")
        cards.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for index in range(4):
            cards.columnconfigure(index, weight=1, uniform="result_cards")
        for column, (title, key) in enumerate(
            (
                ("Polarización", "polarization"),
                ("Costo utilizado", "cost"),
                ("Mediana", "median"),
                ("Tiempo solver", "time"),
            )
        ):
            metric_card(cards, column, title, self.values[key])

        compliance = ttk.Frame(
            self,
            style="CompliancePanel.TFrame",
            padding=(12, 9),
        )
        compliance.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        compliance.columnconfigure(1, weight=1)
        ttk.Label(
            compliance,
            text="Verificación de restricciones",
            style="ComplianceTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=(0, 14))
        self.compliance_summary = tk.StringVar(value="Ejecute una instancia")
        ttk.Label(
            compliance,
            textvariable=self.compliance_summary,
            style="ComplianceSummary.TLabel",
        ).grid(row=0, column=1, sticky="w")

        self.compliance_items: list[tuple[tk.StringVar, tk.StringVar]] = []
        checks = ttk.Frame(compliance, style="Compliance.TFrame")
        checks.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(7, 0))
        for column in range(2):
            checks.columnconfigure(column, weight=1, uniform="compliance")
        for index in range(6):
            status = tk.StringVar(value="○")
            text = tk.StringVar(value="Pendiente")
            item = ttk.Frame(checks, style="Compliance.TFrame")
            item.grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=(0 if index % 2 == 0 else 14, 0),
                pady=(0, 4),
            )
            ttk.Label(
                item,
                textvariable=status,
                style="CompliancePending.TLabel",
                width=2,
            ).pack(side=tk.LEFT)
            ttk.Label(
                item,
                textvariable=text,
                style="ComplianceItem.TLabel",
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.compliance_items.append((status, text))

        panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.grid(row=2, column=0, sticky="nsew")
        movements_frame = ttk.Frame(panes, style="Surface.TFrame")
        distribution_frame = ttk.Frame(panes, style="Surface.TFrame")
        panes.add(movements_frame, weight=3)
        panes.add(distribution_frame, weight=2)

        movements_frame.columnconfigure(0, weight=1)
        movements_frame.rowconfigure(1, weight=1)
        ttk.Label(
            movements_frame,
            text="Matriz de movimientos x[i,j]",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 7))
        self.movement_table = MatrixTable(movements_frame, column_width=92)
        self.movement_table.grid(row=1, column=0, sticky="nsew")

        distribution_frame.columnconfigure(0, weight=1)
        distribution_frame.rowconfigure(1, weight=1)
        distribution_frame.rowconfigure(2, weight=2)
        ttk.Label(
            distribution_frame,
            text="Distribución final",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=(14, 0), pady=(0, 7))
        self.final_tree = tree_with_scrollbars(
            distribution_frame,
            columns=("opinion", "initial", "final"),
            row=1,
            padx=(14, 0),
            height=4,
        )
        for key, title, width in (
            ("opinion", "Opinión", 80),
            ("initial", "Inicial", 90),
            ("final", "Final", 90),
        ):
            self.final_tree.heading(key, text=title)
            self.final_tree.column(key, width=width, anchor=tk.CENTER)

        self.chart = DistributionChart(distribution_frame)
        self.chart.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(14, 0),
            pady=(12, 0),
        )

    def show_result(
        self,
        instance: MinPolInstance,
        result: MinPolResult,
    ) -> None:
        """Muestra una solución y recalcula sus restricciones.

        Args:
            instance: Datos originales de la instancia.
            result: Resultado obtenido con MiniZinc.

        Returns:
            None.

        Example:
            >>> # vista.show_result(instancia, resultado)
        """
        self.values["polarization"].set(fraction_text(result.polarization))
        self.values["cost"].set(fraction_text(result.total_cost))
        self.values["median"].set(
            f"v{result.median_index} = {fraction_text(result.median_value)}"
        )
        solve_time = result.statistics.get("solveTime")
        self.values["time"].set(f"{solve_time} s" if solve_time else "—")

        self.movement_table.show(result.movements)
        clear_tree(self.final_tree)
        for index, final_value in enumerate(result.final_distribution):
            self.final_tree.insert(
                "",
                tk.END,
                values=(index + 1, instance.p[index], final_value),
            )
        self.chart.show(result.final_distribution)

        checks = evaluate_compliance(instance, result)
        passed = sum(check.passed for check in checks)
        self.compliance_summary.set(
            f"{passed}/{len(checks)} restricciones satisfechas"
        )
        for (status, text), check in zip(self.compliance_items, checks):
            status.set("✓" if check.passed else "✕")
            text.set(f"{check.name}: {check.detail}")

    def clear(self) -> None:
        """Restablece la vista al estado sin solución.

        Returns:
            None.

        Example:
            >>> # vista.clear()
        """
        for variable in self.values.values():
            variable.set("—")
        self.movement_table.clear()
        clear_tree(self.final_tree)
        self.chart.clear()
        self.compliance_summary.set("Ejecute una instancia")
        for status, text in self.compliance_items:
            status.set("○")
            text.set("Pendiente")
