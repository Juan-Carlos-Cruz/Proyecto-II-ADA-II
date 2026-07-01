"""Panel lateral de carga, configuración y ejecución."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk


class Sidebar(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        on_load: Callable[[], None],
        on_generate: Callable[[], None],
        on_solve: Callable[[], None],
    ) -> None:
        """Construye los controles de carga, solver y ejecución.

        Args:
            parent: Contenedor Tkinter propietario.
            on_load: Acción para cargar una instancia.
            on_generate: Acción para generar el DZN.
            on_solve: Acción para resolver la instancia.

        Returns:
            None.

        Example:
            >>> # panel = Sidebar(root, cargar, generar, resolver)
        """
        super().__init__(
            parent,
            style="Sidebar.TFrame",
            width=270,
            padding=20,
        )
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)

        self.solver = tk.StringVar(value="Chuffed")
        self.file_name = tk.StringVar(value="Ningún archivo cargado")
        self.file_path = tk.StringVar(value="")

        ttk.Label(
            self,
            text="MinPol",
            style="Sidebar.TLabel",
            font=("TkDefaultFont", 22, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text="Optimización de polarización",
            style="SidebarMuted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(0, 24))

        ttk.Label(
            self,
            text="INSTANCIA",
            style="SidebarMuted.TLabel",
            font=("TkDefaultFont", 8, "bold"),
        ).grid(row=2, column=0, sticky="w")
        ttk.Label(
            self,
            textvariable=self.file_name,
            style="Sidebar.TLabel",
            font=("TkDefaultFont", 10, "bold"),
            wraplength=225,
        ).grid(row=3, column=0, sticky="ew", pady=(5, 2))
        ttk.Label(
            self,
            textvariable=self.file_path,
            style="SidebarMuted.TLabel",
            wraplength=225,
        ).grid(row=4, column=0, sticky="ew", pady=(0, 14))

        self.load_button = ttk.Button(
            self,
            text="Cargar archivo .pca",
            style="Secondary.TButton",
            command=on_load,
        )
        self.load_button.grid(row=5, column=0, sticky="ew", pady=(0, 18))

        ttk.Separator(self).grid(row=6, column=0, sticky="ew", pady=(0, 18))
        ttk.Label(
            self,
            text="SOLVER",
            style="SidebarMuted.TLabel",
            font=("TkDefaultFont", 8, "bold"),
        ).grid(row=7, column=0, sticky="w", pady=(0, 5))
        self.solver_box = ttk.Combobox(
            self,
            textvariable=self.solver,
            values=("Chuffed", "HiGHS", "COIN-BC"),
            state="readonly",
        )
        self.solver_box.grid(row=8, column=0, sticky="ew", pady=(0, 14))

        self.generate_button = ttk.Button(
            self,
            text="Generar DatosProyecto.dzn",
            style="Secondary.TButton",
            command=on_generate,
            state=tk.DISABLED,
        )
        self.generate_button.grid(row=9, column=0, sticky="ew", pady=(0, 8))

        self.run_button = ttk.Button(
            self,
            text="Resolver instancia",
            style="Primary.TButton",
            command=on_solve,
            state=tk.DISABLED,
        )
        self.run_button.grid(row=10, column=0, sticky="ew")

        self.progress = ttk.Progressbar(
            self,
            mode="indeterminate",
            style="Horizontal.TProgressbar",
        )
        self.progress.grid(row=11, column=0, sticky="ew", pady=(14, 0))

        self.rowconfigure(12, weight=1)
        ttk.Label(
            self,
            text="Proyecto.mzn",
            style="SidebarMuted.TLabel",
        ).grid(row=13, column=0, sticky="sw")
        ttk.Label(
            self,
            text="Modelo entero lineal",
            style="SidebarMuted.TLabel",
        ).grid(row=14, column=0, sticky="sw")

    def show_file(self, path: Path) -> None:
        """Muestra el nombre y ubicación del PCA cargado.

        Args:
            path: Ruta absoluta del archivo.

        Returns:
            None.

        Example:
            >>> # panel.show_file(Path("entrada.pca"))
        """
        self.file_name.set(path.name)
        self.file_path.set(str(path.parent))

    def set_instance_available(self, available: bool) -> None:
        """Activa acciones que requieren una instancia.

        Args:
            available: Indica si existe una instancia válida.

        Returns:
            None.

        Example:
            >>> # panel.set_instance_available(True)
        """
        state = tk.NORMAL if available else tk.DISABLED
        self.generate_button.configure(state=state)
        self.run_button.configure(state=state)

    def set_busy(self, busy: bool, has_instance: bool) -> None:
        """Alterna los controles entre ejecución y reposo.

        Args:
            busy: Indica si el solver está trabajando.
            has_instance: Indica si puede reactivarse la resolución.

        Returns:
            None.

        Example:
            >>> # panel.set_busy(True, has_instance=True)
        """
        if busy:
            self.run_button.configure(state=tk.DISABLED)
            self.generate_button.configure(state=tk.DISABLED)
            self.load_button.configure(state=tk.DISABLED)
            self.solver_box.configure(state=tk.DISABLED)
            self.progress.start(12)
            return

        self.set_instance_available(has_instance)
        self.load_button.configure(state=tk.NORMAL)
        self.solver_box.configure(state="readonly")
        self.progress.stop()
