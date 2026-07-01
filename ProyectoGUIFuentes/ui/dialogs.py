"""Ventanas secundarias de la interfaz."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .theme import COLORS


class RawOutputDialog(tk.Toplevel):
    """Presenta y permite copiar la salida original de MiniZinc."""

    def __init__(self, parent: tk.Misc, output: str) -> None:
        """Inicializa el diálogo de salida técnica.

        Args:
            parent: Ventana propietaria.
            output: Texto original de MiniZinc.

        Returns:
            None.

        Example:
            >>> # dialogo = RawOutputDialog(root, salida)
        """
        super().__init__(parent)
        self.output = output
        self.title("Salida técnica de MiniZinc")
        self.geometry("900x620")
        self.minsize(680, 440)
        self.transient(parent.winfo_toplevel())
        self.configure(background=COLORS["background"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_header()
        self._build_text()
        self._build_actions()

    def _build_header(self) -> None:
        """Construye el encabezado del diálogo.

        Returns:
            None.

        Example:
            >>> # dialogo._build_header()
        """
        header = tk.Frame(
            self,
            background=COLORS["sidebar"],
            padx=18,
            pady=13,
        )
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(
            header,
            text="Salida técnica completa",
            background=COLORS["sidebar"],
            foreground="#ffffff",
            font=("TkDefaultFont", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Registro original producido por MiniZinc y el solver",
            background=COLORS["sidebar"],
            foreground="#b8c4d8",
            font=("TkDefaultFont", 9),
        ).pack(anchor="w", pady=(2, 0))

    def _build_text(self) -> None:
        """Construye el visor desplazable de texto.

        Returns:
            None.

        Example:
            >>> # dialogo._build_text()
        """
        frame = ttk.Frame(self, style="App.TFrame", padding=(14, 14, 14, 8))
        frame.grid(row=1, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        text = tk.Text(
            frame,
            wrap=tk.NONE,
            font=("TkFixedFont", 9),
            background="#0f172a",
            foreground="#dbeafe",
            insertbackground="#ffffff",
            selectbackground="#1d4ed8",
            relief=tk.FLAT,
            padx=14,
            pady=12,
        )
        y_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        x_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview)
        text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        text.insert("1.0", self.output)
        text.configure(state=tk.DISABLED)

    def _build_actions(self) -> None:
        """Construye los botones de copiar y cerrar.

        Returns:
            None.

        Example:
            >>> # dialogo._build_actions()
        """
        actions = ttk.Frame(self, style="App.TFrame", padding=(14, 0, 14, 14))
        actions.grid(row=2, column=0, sticky="ew")
        ttk.Button(
            actions,
            text="Copiar salida",
            command=self._copy,
        ).pack(side=tk.LEFT)
        ttk.Button(
            actions,
            text="Cerrar",
            style="Primary.TButton",
            command=self.destroy,
        ).pack(side=tk.RIGHT)

    def _copy(self) -> None:
        """Copia la salida técnica al portapapeles.

        Returns:
            None.

        Example:
            >>> # dialogo._copy()
        """
        self.clipboard_clear()
        self.clipboard_append(self.output)
        messagebox.showinfo(
            "Salida copiada",
            "La salida técnica se copió al portapapeles.",
            parent=self,
        )
