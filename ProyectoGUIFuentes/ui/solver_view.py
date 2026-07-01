"""Vista resumida de métricas y salida técnica del solver."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from result_parser import MinPolResult

from .components import ScrollableFrame, clear_tree, tree_with_scrollbars
from .dialogs import RawOutputDialog
from .theme import COLORS


class SolverView(ttk.Frame):
    PREFERRED_METRICS = (
        "objective",
        "objectiveBound",
        "nodes",
        "failures",
        "restarts",
        "solveTime",
        "flatTime",
        "peakDepth",
        "propagations",
        "nSolutions",
    )

    def __init__(
        self,
        parent: tk.Misc,
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        """Inicializa el panel de métricas del solver.

        Args:
            parent: Contenedor Tkinter propietario.
            on_status: Acción opcional para notificar mensajes.

        Returns:
            None.

        Example:
            >>> # vista = SolverView(notebook)
        """
        super().__init__(parent, style="Surface.TFrame", padding=16)
        self.on_status = on_status
        self.raw_output = ""
        self.values = {
            "icon": tk.StringVar(value="○"),
            "status": tk.StringVar(value="Sin ejecución"),
            "solver": tk.StringVar(value="—"),
            "objective": tk.StringVar(value="—"),
            "bound": tk.StringVar(value="—"),
            "nodes": tk.StringVar(value="—"),
            "failures": tk.StringVar(value="—"),
            "restarts": tk.StringVar(value="—"),
            "solve_time": tk.StringVar(value="—"),
            "flat_time": tk.StringVar(value="—"),
            "variables": tk.StringVar(value="—"),
            "constraints": tk.StringVar(value="—"),
            "solutions": tk.StringVar(value="—"),
        }
        self._build()

    def _build(self) -> None:
        """Construye tablas, resumen y acciones.

        Returns:
            None.

        Example:
            >>> # vista._build()
        """
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        ttk.Label(
            self,
            text="Análisis de la ejecución",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text=(
                "Resumen de optimalidad, rendimiento y tamaño del modelo. "
                "La salida técnica permanece disponible bajo demanda."
            ),
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.grid(row=2, column=0, sticky="nsew")
        stats_frame = ttk.Frame(panes, style="Surface.TFrame")
        summary_host = ttk.Frame(
            panes,
            style="Surface.TFrame",
            padding=(16, 0, 0, 0),
        )
        panes.add(stats_frame, weight=1)
        panes.add(summary_host, weight=2)

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(1, weight=1)
        ttk.Label(
            stats_frame,
            text="Todas las métricas",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 7))
        self.stats_tree = tree_with_scrollbars(
            stats_frame,
            columns=("metric", "value"),
            row=1,
        )
        self.stats_tree.heading("metric", text="Métrica")
        self.stats_tree.heading("value", text="Valor")
        self.stats_tree.column("metric", width=160, anchor=tk.W)
        self.stats_tree.column("value", width=110, anchor=tk.CENTER)

        summary_host.columnconfigure(0, weight=1)
        summary_host.rowconfigure(1, weight=1)
        ttk.Label(
            summary_host,
            text="Resumen de ejecución",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 7))
        scrolling = ScrollableFrame(summary_host)
        scrolling.grid(row=1, column=0, sticky="nsew")
        self.summary_canvas = scrolling.canvas
        summary = scrolling.content
        summary.columnconfigure(0, weight=1)

        self._build_status_card(summary)
        self._build_metric_tiles(summary)
        self._build_search_line(summary)
        self._build_actions(summary)

    def _build_status_card(self, parent: tk.Frame) -> None:
        """Construye la tarjeta de estado y solver.

        Args:
            parent: Contenedor de la tarjeta.

        Returns:
            None.

        Example:
            >>> # vista._build_status_card(frame)
        """
        card = tk.Frame(
            parent,
            background="#ecfdf5",
            highlightthickness=1,
            highlightbackground="#a7f3d0",
            padx=15,
            pady=9,
        )
        card.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        card.columnconfigure(1, weight=1)
        tk.Label(
            card,
            textvariable=self.values["icon"],
            background="#ecfdf5",
            foreground=COLORS["success"],
            font=("TkDefaultFont", 20, "bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(0, 12))
        tk.Label(
            card,
            textvariable=self.values["status"],
            background="#ecfdf5",
            foreground="#065f46",
            font=("TkDefaultFont", 12, "bold"),
        ).grid(row=0, column=1, sticky="w")
        tk.Label(
            card,
            textvariable=self.values["solver"],
            background="#ecfdf5",
            foreground="#047857",
            font=("TkDefaultFont", 9),
        ).grid(row=1, column=1, sticky="w", pady=(2, 0))

    def _build_metric_tiles(self, parent: tk.Frame) -> None:
        """Construye las tarjetas de métricas principales.

        Args:
            parent: Contenedor de las tarjetas.

        Returns:
            None.

        Example:
            >>> # vista._build_metric_tiles(frame)
        """
        tiles = tk.Frame(parent, background=COLORS["surface"])
        tiles.grid(row=1, column=0, sticky="ew")
        tiles.columnconfigure(0, weight=1, uniform="detail_tiles")
        tiles.columnconfigure(1, weight=1, uniform="detail_tiles")
        definitions = (
            ("Objetivo escalado", "objective"),
            ("Cota escalada", "bound"),
            ("Nodos explorados", "nodes"),
            ("Soluciones", "solutions"),
            ("Tiempo de resolución", "solve_time"),
            ("Tiempo de traducción", "flat_time"),
            ("Variables enteras", "variables"),
            ("Restricciones enteras", "constraints"),
        )
        for index, (title, key) in enumerate(definitions):
            self._detail_tile(
                tiles,
                row=index // 2,
                column=index % 2,
                title=title,
                variable=self.values[key],
            )

    def _detail_tile(
        self,
        parent: tk.Frame,
        row: int,
        column: int,
        title: str,
        variable: tk.StringVar,
    ) -> None:
        """Añade una tarjeta individual al resumen.

        Args:
            parent: Contenedor propietario.
            row: Fila de cuadrícula.
            column: Columna de cuadrícula.
            title: Etiqueta de la métrica.
            variable: Variable con su valor.

        Returns:
            None.

        Example:
            >>> # vista._detail_tile(frame, 0, 0, "Nodos", nodos)
        """
        tile = tk.Frame(
            parent,
            background="#f8fafc",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=12,
            pady=7,
        )
        tile.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=(0 if column == 0 else 5, 5 if column == 0 else 0),
            pady=(0, 5),
        )
        tk.Label(
            tile,
            text=title,
            background="#f8fafc",
            foreground=COLORS["muted"],
            font=("TkDefaultFont", 8),
        ).pack(anchor="w")
        tk.Label(
            tile,
            textvariable=variable,
            background="#f8fafc",
            foreground=COLORS["text"],
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w", pady=(2, 0))

    def _build_search_line(self, parent: tk.Frame) -> None:
        """Construye el resumen de fallos y reinicios.

        Args:
            parent: Contenedor propietario.

        Returns:
            None.

        Example:
            >>> # vista._build_search_line(frame)
        """
        line = tk.Frame(
            parent,
            background="#f8fafc",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            padx=12,
            pady=9,
        )
        line.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        line.columnconfigure(1, weight=1)
        line.columnconfigure(3, weight=1)
        tk.Label(
            line,
            text="Indicadores de búsqueda",
            background="#f8fafc",
            foreground=COLORS["muted"],
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))
        for column, title, key in (
            (0, "Fallos", "failures"),
            (2, "Reinicios", "restarts"),
        ):
            tk.Label(
                line,
                text=title,
                background="#f8fafc",
                foreground=COLORS["muted"],
                font=("TkDefaultFont", 9),
            ).grid(row=1, column=column, sticky="w")
            tk.Label(
                line,
                textvariable=self.values[key],
                background="#f8fafc",
                foreground=COLORS["text"],
                font=("TkDefaultFont", 9, "bold"),
            ).grid(row=1, column=column + 1, sticky="w", padx=(8, 20))

    def _build_actions(self, parent: tk.Frame) -> None:
        """Construye las acciones sobre la salida.

        Args:
            parent: Contenedor propietario.

        Returns:
            None.

        Example:
            >>> # vista._build_actions(frame)
        """
        actions = ttk.Frame(parent, style="Surface.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(9, 5))
        ttk.Button(
            actions,
            text="Ver salida técnica completa",
            style="Outline.TButton",
            command=self.open_raw_output,
        ).pack(side=tk.LEFT)
        ttk.Button(
            actions,
            text="Copiar resumen",
            command=self.copy_summary,
        ).pack(side=tk.LEFT, padx=(8, 0))

    def show_result(self, result: MinPolResult, solver: str) -> None:
        """Muestra el certificado y las estadísticas de una ejecución.

        Args:
            result: Resultado estructurado de MiniZinc.
            solver: Nombre del solver ejecutado.

        Returns:
            None.

        Example:
            >>> # vista.show_result(resultado, "HiGHS")
        """
        statistics = result.statistics
        self.raw_output = result.raw_output
        self.values["icon"].set("✓")
        self.values["status"].set(
            "Óptimo certificado"
            if "==========" in result.raw_output
            else "Solución factible"
        )
        self.values["solver"].set(f"Solver: {solver}")
        self.values["objective"].set(
            statistics.get("objective", str(result.polarization))
        )
        self.values["bound"].set(statistics.get("objectiveBound", "—"))
        self.values["nodes"].set(statistics.get("nodes", "—"))
        self.values["failures"].set(statistics.get("failures", "No reportado"))
        self.values["restarts"].set(statistics.get("restarts", "No reportado"))
        self.values["solve_time"].set(self._seconds(statistics.get("solveTime")))
        self.values["flat_time"].set(self._seconds(statistics.get("flatTime")))
        self.values["variables"].set(
            statistics.get("flatIntVars", statistics.get("intVars", "—"))
        )
        self.values["constraints"].set(
            statistics.get("flatIntConstraints", "—")
        )
        self.values["solutions"].set(statistics.get("nSolutions", "1"))

        clear_tree(self.stats_tree)
        added: set[str] = set()
        for key in self.PREFERRED_METRICS:
            if key in statistics:
                self.stats_tree.insert("", tk.END, values=(key, statistics[key]))
                added.add(key)
        for key in sorted(statistics):
            if key not in added:
                self.stats_tree.insert("", tk.END, values=(key, statistics[key]))

    def clear(self) -> None:
        """Restablece métricas y salida técnica.

        Returns:
            None.

        Example:
            >>> # vista.clear()
        """
        for key, variable in self.values.items():
            if key == "icon":
                variable.set("○")
            elif key == "status":
                variable.set("Sin ejecución")
            else:
                variable.set("—")
        clear_tree(self.stats_tree)
        self.raw_output = ""

    @staticmethod
    def _seconds(value: str | None) -> str:
        """Añade la unidad de segundos a una métrica opcional.

        Args:
            value: Valor textual reportado por MiniZinc.

        Returns:
            Texto con unidad o un marcador vacío.

        Example:
            >>> SolverView._seconds("0.5")
            '0.5 s'
        """
        return f"{value} s" if value else "—"

    def copy_summary(self) -> None:
        """Copia al portapapeles el resumen de la ejecución.

        Returns:
            None.

        Example:
            >>> # vista.copy_summary()
        """
        if not self._require_output("Sin resultados"):
            return
        summary = "\n".join(
            [
                f"Estado: {self.values['status'].get()}",
                self.values["solver"].get(),
                f"Objetivo escalado: {self.values['objective'].get()}",
                f"Cota escalada: {self.values['bound'].get()}",
                f"Nodos: {self.values['nodes'].get()}",
                f"Soluciones: {self.values['solutions'].get()}",
                f"Tiempo solver: {self.values['solve_time'].get()}",
                f"Tiempo de traducción: {self.values['flat_time'].get()}",
                f"Variables enteras: {self.values['variables'].get()}",
                f"Restricciones enteras: {self.values['constraints'].get()}",
                f"Fallos: {self.values['failures'].get()}",
                f"Reinicios: {self.values['restarts'].get()}",
            ]
        )
        self.clipboard_clear()
        self.clipboard_append(summary)
        if self.on_status:
            self.on_status("Resumen de ejecución copiado al portapapeles.")

    def open_raw_output(self) -> None:
        """Abre el diálogo con la salida original.

        Returns:
            None.

        Example:
            >>> # vista.open_raw_output()
        """
        if not self._require_output("Sin salida técnica"):
            return
        RawOutputDialog(self, self.raw_output)

    def _require_output(self, title: str) -> bool:
        """Comprueba que haya una ejecución antes de una acción.

        Args:
            title: Título del aviso cuando no hay salida.

        Returns:
            ``True`` si existe salida técnica.

        Example:
            >>> # disponible = vista._require_output("Sin resultados")
        """
        if self.raw_output:
            return True
        messagebox.showinfo(
            title,
            "Primero debe resolver una instancia.",
            parent=self.winfo_toplevel(),
        )
        return False
