"""Ejecución segura del modelo MiniZinc mediante línea de comandos."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class MiniZincRunError(RuntimeError):
    pass


def find_minizinc() -> str:
    """Localiza el ejecutable MiniZinc de forma portable.

    Returns:
        Ruta o nombre ejecutable encontrado.

    Example:
        >>> # ruta = find_minizinc()
    """
    configured = os.environ.get("MINIZINC_EXECUTABLE")
    if configured and Path(configured).is_file():
        return configured

    executable = shutil.which("minizinc")
    if executable:
        return executable

    # VS Code y otros lanzadores gráficos pueden conservar un PATH anterior
    # aunque ~/.bashrc ya haya sido actualizado. Buscar también instalaciones
    # locales habituales permite ejecutar la interfaz sin configuración extra.
    local_opt = Path.home() / ".local" / "opt"
    candidates = [
        *sorted(
            local_opt.glob("minizinc-*/bin/minizinc"),
            reverse=True,
        ),
        Path.home() / ".local" / "bin" / "minizinc",
        Path("/opt/minizinc/bin/minizinc"),
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)

    raise MiniZincRunError(
        "No se encontró el ejecutable 'minizinc'. Instale MiniZinc y agréguelo "
        "al PATH, o defina la variable MINIZINC_EXECUTABLE."
    )


def run_minizinc(
    model_path: str | Path,
    data_path: str | Path,
    solver: str = "Chuffed",
    timeout_seconds: int = 300,
) -> str:
    """Ejecuta MiniZinc con estadísticas y límite de tiempo.

    Args:
        model_path: Ruta del modelo MZN.
        data_path: Ruta del archivo DZN.
        solver: Nombre del solver registrado en MiniZinc.
        timeout_seconds: Tiempo máximo permitido.

    Returns:
        Salida estándar y diagnósticos producidos por MiniZinc.

    Example:
        >>> # salida = run_minizinc("Proyecto.mzn", "DatosProyecto.dzn")
    """
    executable = find_minizinc()
    model = Path(model_path).resolve()
    data = Path(data_path).resolve()
    if not model.is_file():
        raise MiniZincRunError(f"No existe el modelo: {model}")
    if not data.is_file():
        raise MiniZincRunError(f"No existe el archivo de datos: {data}")

    command = [
        executable,
        "--solver",
        solver,
        "--statistics",
        str(model),
        str(data),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise MiniZincRunError(
            f"MiniZinc superó el límite de {timeout_seconds} segundos."
        ) from exc
    except OSError as exc:
        raise MiniZincRunError(f"No se pudo ejecutar MiniZinc: {exc}") from exc

    combined = completed.stdout
    if completed.stderr:
        combined += ("\n" if combined else "") + completed.stderr
    if completed.returncode != 0:
        raise MiniZincRunError(
            f"MiniZinc terminó con código {completed.returncode}:\n{combined}"
        )
    return combined
