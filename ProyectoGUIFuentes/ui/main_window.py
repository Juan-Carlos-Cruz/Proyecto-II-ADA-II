"""Ventana principal y coordinación del flujo de la aplicación."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from minizinc_runner import MiniZincRunError, run_minizinc
from pca_parser import MinPolInstance, PCAValidationError, read_pca, write_dzn
from result_parser import MinPolResult, ResultParseError, fraction_text, parse_minizinc_output

from .input_view import InputView
from .result_view import ResultView
from .sidebar import Sidebar
from .solver_view import SolverView
from .theme import COLORS, configure_styles


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "Proyecto.mzn"
GENERATED_DZN = PROJECT_ROOT / "DatosProyecto.dzn"


class MinPolApp(tk.Tk):
    def __init__(self) -> None:
        """Inicializa la ventana, el estado y las vistas de MinPol.

        Returns:
            None.

        Example:
            >>> # app = MinPolApp()
        """
        super().__init__()
        self.title("MinPol — Minimización de la polarización")
        self.geometry("1180x760")
        self.minsize(940, 640)
        self.configure(background=COLORS["background"])

        self.instance: MinPolInstance | None = None
        self.source_path: Path | None = None
        self.status = tk.StringVar(value="Seleccione una instancia para comenzar.")

        configure_styles(self)
        self._build_ui()

    def _build_ui(self) -> None:
        """Construye la distribución visual de la ventana.

        Returns:
            None.

        Example:
            >>> # app._build_ui()
        """
        container = ttk.Frame(self, style="App.TFrame")
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self.sidebar = Sidebar(
            container,
            on_load=self.load_file,
            on_generate=self.generate,
            on_solve=self.solve,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        workspace = ttk.Frame(
            container,
            style="App.TFrame",
            padding=(24, 20, 24, 16),
        )
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(2, weight=1)

        ttk.Label(
            workspace,
            text="Minimización de la polarización",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            workspace,
            text="Cargue una población, ejecute el modelo y analice la solución.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

        self.notebook = ttk.Notebook(workspace)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.input_view = InputView(self.notebook)
        self.result_view = ResultView(self.notebook)
        self.solver_view = SolverView(
            self.notebook,
            on_status=self.set_status,
        )
        self.notebook.add(self.input_view, text="Datos de entrada")
        self.notebook.add(self.result_view, text="Solución")
        self.notebook.add(self.solver_view, text="Detalles del solver")

        ttk.Label(
            workspace,
            textvariable=self.status,
            style="Status.TLabel",
        ).grid(row=3, column=0, sticky="ew", pady=(10, 0))

    def set_status(self, message: str) -> None:
        """Actualiza el mensaje inferior de estado.

        Args:
            message: Mensaje que se mostrará al usuario.

        Returns:
            None.

        Example:
            >>> # app.set_status("Instancia validada.")
        """
        self.status.set(message)

    def load_file(self) -> None:
        """Solicita un PCA, lo valida y actualiza las vistas.

        Returns:
            None.

        Example:
            >>> # app.load_file()
        """
        selected = filedialog.askopenfilename(
            title="Seleccionar instancia MinPol",
            filetypes=(("Instancias PCA", "*.pca"), ("Todos los archivos", "*.*")),
        )
        if not selected:
            return
        try:
            instance = read_pca(selected)
        except PCAValidationError as exc:
            messagebox.showerror("Archivo inválido", str(exc), parent=self)
            self.set_status("La instancia seleccionada no es válida.")
            return

        self.instance = instance
        self.source_path = Path(selected).resolve()
        self.sidebar.show_file(self.source_path)
        self.sidebar.set_instance_available(True)
        self.input_view.show_instance(instance)
        self.result_view.clear()
        self.solver_view.clear()
        self.notebook.select(self.input_view)
        self.set_status("Instancia validada correctamente. Ya puede resolverla.")

    def _reload_and_generate(self) -> MinPolInstance:
        """Recarga la fuente seleccionada y genera ``DatosProyecto.dzn``.

        Returns:
            Instancia validada que se escribió en DZN.

        Example:
            >>> # instancia = app._reload_and_generate()
        """
        if not self.source_path:
            raise PCAValidationError("Primero debe cargar un archivo .pca.")
        instance = read_pca(self.source_path)
        write_dzn(instance, GENERATED_DZN)
        self.instance = instance
        return instance

    def generate(self) -> None:
        """Genera el DZN solicitado y notifica el resultado.

        Returns:
            None.

        Example:
            >>> # app.generate()
        """
        try:
            self._reload_and_generate()
        except PCAValidationError as exc:
            messagebox.showerror("No se pudo generar el DZN", str(exc), parent=self)
            return
        self.set_status(f"Datos generados en {GENERATED_DZN.name}.")
        messagebox.showinfo(
            "Conversión completada",
            f"Se creó correctamente:\n{GENERATED_DZN}",
            parent=self,
        )

    def solve(self) -> None:
        """Valida la instancia e inicia el solver en segundo plano.

        Returns:
            None.

        Example:
            >>> # app.solve()
        """
        try:
            instance = self._reload_and_generate()
        except PCAValidationError as exc:
            messagebox.showerror("Datos inválidos", str(exc), parent=self)
            return

        solver = self.sidebar.solver.get()
        self.sidebar.set_busy(True, has_instance=True)
        self.set_status(f"Resolviendo con {solver}…")
        threading.Thread(
            target=self._solve_worker,
            args=(instance.m, solver),
            daemon=True,
        ).start()

    def _solve_worker(self, m: int, solver: str) -> None:
        """Ejecuta MiniZinc fuera del hilo gráfico.

        Args:
            m: Número de opiniones esperado en la salida.
            solver: Solver seleccionado por el usuario.

        Returns:
            None.

        Example:
            >>> # app._solve_worker(5, "HiGHS")
        """
        try:
            output = run_minizinc(MODEL_PATH, GENERATED_DZN, solver=solver)
            result = parse_minizinc_output(output, m)
        except (MiniZincRunError, ResultParseError) as exc:
            self.after(0, self._solve_failed, str(exc))
            return
        self.after(0, self._show_result, result, solver)

    def _solve_failed(self, message: str) -> None:
        """Restaura la interfaz después de un error del solver.

        Args:
            message: Descripción del error.

        Returns:
            None.

        Example:
            >>> # app._solve_failed("MiniZinc no disponible")
        """
        self.sidebar.set_busy(False, has_instance=self.instance is not None)
        self.set_status("La ejecución terminó con error.")
        messagebox.showerror("Error al resolver", message, parent=self)

    def _show_result(self, result: MinPolResult, solver: str | None = None) -> None:
        """Distribuye una solución válida entre las vistas.

        Args:
            result: Resultado estructurado de MiniZinc.
            solver: Solver usado; si se omite, toma el seleccionado.

        Returns:
            None.

        Example:
            >>> # app._show_result(resultado, "HiGHS")
        """
        selected_solver = solver or self.sidebar.solver.get()
        self.sidebar.set_busy(False, has_instance=self.instance is not None)
        if self.instance is None:
            self._solve_failed("No hay una instancia cargada.")
            return

        self.result_view.show_result(self.instance, result)
        self.solver_view.show_result(result, selected_solver)
        self.notebook.select(self.result_view)
        self.set_status(
            f"Solución óptima obtenida con {selected_solver}: "
            f"polarización {fraction_text(result.polarization)}."
        )


def main() -> None:
    """Crea la aplicación e inicia el bucle de eventos.

    Returns:
        None.

    Example:
        Desde la raíz del proyecto::

            python3 ProyectoGUIFuentes/app.py
    """
    MinPolApp().mainloop()
