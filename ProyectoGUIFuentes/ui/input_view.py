"""Vista de parámetros y matriz de costos."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from mpl_parser import MinPolInstance, decimal_text

from .components import MatrixTable, clear_tree, metric_card, tree_with_scrollbars


class InputView(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        """Construye la vista de parámetros y costos.

        Args:
            parent: Contenedor Tkinter propietario.

        Returns:
            None.

        Example:
            >>> # vista = InputView(notebook)
        """
        super().__init__(parent, style="Surface.TFrame", padding=16)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.values = {
            "n": tk.StringVar(value="—"),
            "m": tk.StringVar(value="—"),
            "ct": tk.StringVar(value="—"),
            "max_movs": tk.StringVar(value="—"),
            "total": tk.StringVar(value="—"),
        }

        cards = ttk.Frame(self, style="Surface.TFrame")
        cards.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for index in range(5):
            cards.columnconfigure(index, weight=1, uniform="input_cards")
        for column, (title, key) in enumerate(
            (
                ("Población", "n"),
                ("Opiniones", "m"),
                ("Presupuesto", "ct"),
                ("Máx. movimientos", "max_movs"),
                ("Total en p", "total"),
            )
        ):
            metric_card(cards, column, title, self.values[key])

        body = ttk.PanedWindow(self, orient=tk.VERTICAL)
        body.grid(row=2, column=0, sticky="nsew")
        opinions_frame = ttk.Frame(body, style="Surface.TFrame")
        costs_frame = ttk.Frame(body, style="Surface.TFrame")
        body.add(opinions_frame, weight=1)
        body.add(costs_frame, weight=2)

        opinions_frame.columnconfigure(0, weight=1)
        opinions_frame.rowconfigure(1, weight=1)
        ttk.Label(
            opinions_frame,
            text="Opiniones y distribución inicial",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 7))
        self.opinion_tree = tree_with_scrollbars(
            opinions_frame,
            columns=("opinion", "people", "value", "extra"),
            row=1,
        )
        for key, title, width in (
            ("opinion", "Opinión", 90),
            ("people", "Personas p[i]", 130),
            ("value", "Valor v[i]", 130),
            ("extra", "Costo extra ce[i]", 160),
        ):
            self.opinion_tree.heading(key, text=title)
            self.opinion_tree.column(key, width=width, anchor=tk.CENTER)

        costs_frame.columnconfigure(0, weight=1)
        costs_frame.rowconfigure(1, weight=1)
        ttk.Label(
            costs_frame,
            text="Matriz de costos c[i,j]",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(12, 7))
        self.cost_table = MatrixTable(costs_frame, column_width=100)
        self.cost_table.grid(row=1, column=0, sticky="nsew")

    def show_instance(self, instance: MinPolInstance) -> None:
        """Muestra una instancia validada en tablas y tarjetas.

        Args:
            instance: Instancia que se desea inspeccionar.

        Returns:
            None.

        Example:
            >>> # vista.show_instance(instancia)
        """
        self.values["n"].set(str(instance.n))
        self.values["m"].set(str(instance.m))
        self.values["ct"].set(decimal_text(instance.ct))
        self.values["max_movs"].set(str(instance.max_movs))
        self.values["total"].set(str(sum(instance.p)))

        clear_tree(self.opinion_tree)
        for index in range(instance.m):
            self.opinion_tree.insert(
                "",
                tk.END,
                values=(
                    index + 1,
                    instance.p[index],
                    decimal_text(instance.v[index]),
                    decimal_text(instance.ce[index]),
                ),
            )
        self.cost_table.show(
            [tuple(map(decimal_text, row)) for row in instance.c]
        )
