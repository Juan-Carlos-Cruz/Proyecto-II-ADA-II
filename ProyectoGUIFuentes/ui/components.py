"""Widgets reutilizables de la interfaz."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Iterable, Sequence
from tkinter import ttk

from .theme import COLORS


def clear_tree(tree: ttk.Treeview | None) -> None:
    """Elimina todas las filas de una tabla si existe.

    Args:
        tree: Tabla que se desea vaciar.

    Returns:
        None.

    Example:
        >>> # clear_tree(tabla)
    """
    if tree is not None:
        tree.delete(*tree.get_children())


def metric_card(
    parent: tk.Misc,
    column: int,
    title: str,
    variable: tk.StringVar,
    total_columns: int = 4,
) -> tk.Frame:
    """Crea una tarjeta de indicador enlazada a una variable.

    Args:
        parent: Contenedor Tkinter propietario.
        column: Columna de la cuadrícula.
        title: Etiqueta del indicador.
        variable: Variable que contiene el valor.
        total_columns: Número total de tarjetas.

    Returns:
        Marco que contiene la tarjeta.

    Example:
        >>> # tarjeta = metric_card(root, 0, "Costo", costo)
    """
    card = tk.Frame(
        parent,
        background=COLORS["surface"],
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        padx=13,
        pady=10,
    )
    card.grid(
        row=0,
        column=column,
        sticky="ew",
        padx=(0 if column == 0 else 5, 0 if column == total_columns - 1 else 5),
    )
    tk.Label(
        card,
        text=title,
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        font=("TkDefaultFont", 9),
    ).pack(anchor="w")
    tk.Label(
        card,
        textvariable=variable,
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("TkDefaultFont", 15, "bold"),
    ).pack(anchor="w", pady=(2, 0))
    return card


def tree_with_scrollbars(
    parent: ttk.Frame,
    columns: tuple[str, ...],
    row: int,
    padx: tuple[int, int] | int = 0,
    height: int | None = None,
) -> ttk.Treeview:
    """Crea una tabla con desplazamiento horizontal y vertical.

    Args:
        parent: Contenedor propietario.
        columns: Identificadores de columnas.
        row: Fila de la cuadrícula.
        padx: Margen horizontal.
        height: Número visible de filas opcional.

    Returns:
        Tabla configurada.

    Example:
        >>> # tabla = tree_with_scrollbars(frame, ("a", "b"), 0)
    """
    frame = ttk.Frame(parent, style="Surface.TFrame")
    frame.grid(row=row, column=0, sticky="nsew", padx=padx)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    options: dict[str, object] = {"columns": columns, "show": "headings"}
    if height is not None:
        options["height"] = height
    tree = ttk.Treeview(frame, **options)
    y_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    x_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    tree.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    return tree


class MatrixTable(ttk.Frame):
    """Tabla de matriz con columnas reconstruibles y desplazamiento."""

    def __init__(
        self,
        parent: tk.Misc,
        origin_title: str = "Origen \\ Destino",
        column_width: int = 96,
    ) -> None:
        """Inicializa una tabla matricial redimensionable.

        Args:
            parent: Contenedor Tkinter propietario.
            origin_title: Título de la primera columna.
            column_width: Ancho de las columnas de datos.

        Returns:
            None.

        Example:
            >>> # tabla = MatrixTable(root)
        """
        super().__init__(parent, style="Surface.TFrame")
        self.origin_title = origin_title
        self.column_width = column_width
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree: ttk.Treeview | None = None
        self.set_size(0)

    def set_size(self, size: int) -> None:
        """Reconstruye la tabla para una matriz cuadrada.

        Args:
            size: Cantidad de filas y columnas.

        Returns:
            None.

        Example:
            >>> # tabla.set_size(5)
        """
        for child in self.winfo_children():
            child.destroy()

        columns = ("origin",) + tuple(f"op{index}" for index in range(1, size + 1))
        tree = ttk.Treeview(self, columns=columns, show="headings")
        y_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        x_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        tree.heading("origin", text=self.origin_title)
        tree.column("origin", width=130, anchor=tk.CENTER)
        for index in range(1, size + 1):
            key = f"op{index}"
            tree.heading(key, text=f"Opinión {index}")
            tree.column(key, width=self.column_width, anchor=tk.CENTER)
        self.tree = tree

    def show(
        self,
        rows: Iterable[Sequence[object]],
        row_prefix: str = "Opinión",
    ) -> None:
        """Carga filas en la tabla matricial.

        Args:
            rows: Filas de valores que se mostrarán.
            row_prefix: Prefijo de las etiquetas de origen.

        Returns:
            None.

        Example:
            >>> # tabla.show([[0, 1], [2, 0]])
        """
        rows = list(rows)
        self.set_size(len(rows))
        if self.tree is None:
            return
        for index, row in enumerate(rows, start=1):
            self.tree.insert(
                "",
                tk.END,
                values=(f"{row_prefix} {index}",) + tuple(row),
            )

    def clear(self) -> None:
        """Vacía la tabla y elimina sus columnas de datos.

        Returns:
            None.

        Example:
            >>> # tabla.clear()
        """
        self.set_size(0)


class DistributionChart(tk.Canvas):
    """Gráfico de barras adaptable para la distribución final."""

    def __init__(self, parent: tk.Misc) -> None:
        """Inicializa el lienzo adaptable del gráfico.

        Args:
            parent: Contenedor Tkinter propietario.

        Returns:
            None.

        Example:
            >>> # grafico = DistributionChart(root)
        """
        super().__init__(
            parent,
            background=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            height=170,
        )
        self.values: tuple[int, ...] = ()
        self.bind("<Configure>", self._schedule_redraw)

    def show(self, values: Sequence[int]) -> None:
        """Establece la distribución y dibuja sus barras.

        Args:
            values: Población final por opinión.

        Returns:
            None.

        Example:
            >>> # grafico.show([18, 2, 0, 0, 0])
        """
        self.values = tuple(values)
        self.draw()

    def clear(self) -> None:
        """Elimina la distribución mostrada.

        Returns:
            None.

        Example:
            >>> # grafico.clear()
        """
        self.values = ()
        self.draw()

    def _schedule_redraw(self, _event=None) -> None:
        """Programa un redibujado después de un cambio de tamaño.

        Args:
            _event: Evento Tkinter no utilizado.

        Returns:
            None.

        Example:
            >>> # grafico._schedule_redraw()
        """
        self.after_idle(self.draw)

    def draw(self) -> None:
        """Dibuja ejes, barras, valores y etiquetas.

        Returns:
            None.

        Example:
            >>> # grafico.draw()
        """
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 120 or height < 80:
            return

        if not self.values:
            self.create_text(
                width / 2,
                height / 2,
                text="La distribución aparecerá después de resolver.",
                fill=COLORS["muted"],
                font=("TkDefaultFont", 9),
                width=width - 40,
            )
            return

        left, right = 34, 18
        top = 20 if height >= 140 else 14
        bottom = 38 if height >= 140 else 30
        chart_width = width - left - right
        chart_height = height - top - bottom
        maximum = max(max(self.values), 1)
        gap = max(5, chart_width * 0.03)
        bar_width = max(
            10,
            (chart_width - gap * (len(self.values) + 1)) / len(self.values),
        )

        self.create_line(
            left,
            top + chart_height,
            width - right,
            top + chart_height,
            fill=COLORS["border"],
        )
        for index, value in enumerate(self.values):
            x0 = left + gap + index * (bar_width + gap)
            x1 = x0 + bar_width
            bar_height = chart_height * value / maximum
            y0 = top + chart_height - bar_height
            y1 = top + chart_height
            self.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=COLORS["chart"],
                outline="",
            )
            self.create_text(
                (x0 + x1) / 2,
                max(y0 - 10, 10),
                text=str(value),
                fill=COLORS["text"],
                font=("TkDefaultFont", 8, "bold"),
            )
            self.create_text(
                (x0 + x1) / 2,
                y1 + 14,
                text=f"O{index + 1}",
                fill=COLORS["muted"],
                font=("TkDefaultFont", 8),
            )


class ScrollableFrame(ttk.Frame):
    """Contenedor vertical que evita recortar contenido en ventanas pequeñas."""

    def __init__(self, parent: tk.Misc) -> None:
        """Inicializa un marco con desplazamiento vertical.

        Args:
            parent: Contenedor Tkinter propietario.

        Returns:
            None.

        Example:
            >>> # marco = ScrollableFrame(root)
        """
        super().__init__(parent, style="Surface.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            background=COLORS["surface"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.content = tk.Frame(
            self.canvas,
            background=COLORS["surface"],
            padx=2,
            pady=1,
        )
        window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(window, width=event.width),
        )
