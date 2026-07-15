"""Lectura, validación y conversión exacta de instancias MinPol MPL."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


class MPLValidationError(ValueError):
    """Indica que un archivo .mpl no cumple el formato del enunciado."""


@dataclass(frozen=True)
class MinPolInstance:
    n: int
    m: int
    p: tuple[int, ...]
    v: tuple[Decimal, ...]
    ce: tuple[Decimal, ...]
    c: tuple[tuple[Decimal, ...], ...]
    ct: Decimal
    max_movs: int
    source: Path | None = None


def _parse_positive_int(text: str, field: str, line: int) -> int:
    """Convierte y valida un entero estrictamente positivo.

    Args:
        text: Texto que contiene el entero.
        field: Nombre del campo para construir mensajes de error.
        line: Número de línea de la entrada.

    Returns:
        Entero validado.

    Example:
        >>> _parse_positive_int("20", "n", 1)
        20
    """
    try:
        value = int(text)
    except ValueError as exc:
        raise MPLValidationError(
            f"Línea {line}: {field} debe ser un entero."
        ) from exc
    if value <= 0:
        raise MPLValidationError(f"Línea {line}: {field} debe ser mayor que 0.")
    return value


def _parse_decimal(text: str, field: str, line: int) -> Decimal:
    """Convierte un texto a un decimal finito.

    Args:
        text: Representación decimal.
        field: Nombre del campo validado.
        line: Número de línea de la entrada.

    Returns:
        Valor decimal exacto.

    Example:
        >>> _parse_decimal("0.25", "v", 4)
        Decimal('0.25')
    """
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise MPLValidationError(
            f"Línea {line}: '{text}' no es un número válido para {field}."
        ) from exc
    if not value.is_finite():
        raise MPLValidationError(
            f"Línea {line}: {field} debe ser un número decimal finito."
        )
    return value


def _split_values(text: str, expected: int, field: str, line: int) -> list[str]:
    """Separa una lista por comas y comprueba su dimensión.

    Args:
        text: Línea con valores separados por comas.
        expected: Cantidad exacta de elementos.
        field: Nombre del campo validado.
        line: Número de línea de la entrada.

    Returns:
        Lista de valores sin espacios laterales.

    Example:
        >>> _split_values("1, 2, 3", 3, "p", 3)
        ['1', '2', '3']
    """
    values = [part.strip() for part in text.split(",")]
    if any(not part for part in values):
        raise MPLValidationError(
            f"Línea {line}: {field} contiene un valor vacío."
        )
    if len(values) != expected:
        raise MPLValidationError(
            f"Línea {line}: {field} debe contener {expected} valores; "
            f"se encontraron {len(values)}."
        )
    return values


def parse_mpl_text(text: str, source: Path | None = None) -> MinPolInstance:
    """Interpreta un MPL completo y valida todos sus campos.

    Args:
        text: Contenido textual de la instancia.
        source: Ruta de origen opcional para trazabilidad.

    Returns:
        Instancia MinPol inmutable con decimales exactos.

    Example:
        >>> instancia = parse_mpl_text("1\\n1\\n1\\n0\\n0\\n0\\n0\\n1")
        >>> (instancia.n, instancia.m, instancia.max_movs)
        (1, 1, 1)
    """

    numbered_lines = [
        (number, content.strip())
        for number, content in enumerate(text.splitlines(), start=1)
        if content.strip()
    ]
    if len(numbered_lines) < 2:
        raise MPLValidationError("El archivo debe contener al menos las líneas n y m.")

    n_line, n_text = numbered_lines[0]
    m_line, m_text = numbered_lines[1]
    n = _parse_positive_int(n_text, "n", n_line)
    m = _parse_positive_int(m_text, "m", m_line)

    expected_lines = 7 + m
    if len(numbered_lines) != expected_lines:
        raise MPLValidationError(
            f"La instancia con m={m} debe contener {expected_lines} líneas "
            f"no vacías; se encontraron {len(numbered_lines)}. "
            "Compruebe el orden: n, m, p, v, ce, matriz c, ct y MaxMovs."
        )

    p_line, p_text = numbered_lines[2]
    p_values = _split_values(p_text, m, "p", p_line)
    p: list[int] = []
    for value in p_values:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise MPLValidationError(
                f"Línea {p_line}: las cantidades de p deben ser enteras."
            ) from exc
        if parsed < 0:
            raise MPLValidationError(
                f"Línea {p_line}: cada valor de p debe ser un entero no negativo."
            )
        p.append(parsed)
    if sum(p) != n:
        raise MPLValidationError(
            f"Línea {p_line}: la suma de p es {sum(p)}, pero n es {n}."
        )

    v_line, v_text = numbered_lines[3]
    v = tuple(
        _parse_decimal(value, "v", v_line)
        for value in _split_values(v_text, m, "v", v_line)
    )
    if any(value < 0 or value > 1 for value in v):
        raise MPLValidationError(
            f"Línea {v_line}: todos los valores de opinión deben estar entre 0 y 1."
        )

    ce_line, ce_text = numbered_lines[4]
    ce = tuple(
        _parse_decimal(value, "ce", ce_line)
        for value in _split_values(ce_text, m, "ce", ce_line)
    )
    if any(value < 0 for value in ce):
        raise MPLValidationError(
            f"Línea {ce_line}: los costos extra no pueden ser negativos."
        )

    matrix: list[tuple[Decimal, ...]] = []
    for row in range(m):
        line, row_text = numbered_lines[5 + row]
        parsed_row = tuple(
            _parse_decimal(value, f"c[{row + 1},j]", line)
            for value in _split_values(row_text, m, "fila de c", line)
        )
        if any(value < 0 for value in parsed_row):
            raise MPLValidationError(
                f"Línea {line}: los costos de movimiento no pueden ser negativos."
            )
        matrix.append(parsed_row)

    ct_line, ct_text = numbered_lines[5 + m]
    ct = _parse_decimal(ct_text, "ct", ct_line)
    if ct < 0:
        raise MPLValidationError(
            f"Línea {ct_line}: el presupuesto ct no puede ser negativo."
        )

    max_movs_line, max_movs_text = numbered_lines[6 + m]
    max_movs = _parse_positive_int(max_movs_text, "MaxMovs", max_movs_line)

    return MinPolInstance(
        n=n,
        m=m,
        p=tuple(p),
        v=v,
        ce=ce,
        c=tuple(matrix),
        ct=ct,
        max_movs=max_movs,
        source=source,
    )


def read_mpl(path: str | Path) -> MinPolInstance:
    """Lee y valida una instancia MPL desde el sistema de archivos.

    Args:
        path: Ruta del archivo MPL.

    Returns:
        Instancia MinPol validada.

    Example:
        >>> instancia = read_mpl("DatosProyecto/ejemplos/ejemplo_pdf.mpl")
        >>> instancia.n
        20
    """
    source = Path(path).expanduser().resolve()
    try:
        text = source.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise MPLValidationError(f"No fue posible leer '{source}': {exc}") from exc
    return parse_mpl_text(text, source=source)


def _required_scale(values: Iterable[Decimal]) -> int:
    """Calcula la menor potencia de diez que representa varios decimales.

    Args:
        values: Valores decimales finitos.

    Returns:
        Factor entero de escalamiento.

    Example:
        >>> _required_scale([Decimal("0.25"), Decimal("1.2")])
        100
    """
    decimal_places = 0
    for value in values:
        exponent = value.normalize().as_tuple().exponent
        decimal_places = max(decimal_places, max(0, -exponent))
    return 10**decimal_places


def _scaled(value: Decimal, scale: int) -> int:
    """Escala exactamente un decimal y exige un resultado entero.

    Args:
        value: Decimal que se desea escalar.
        scale: Factor entero de escalamiento.

    Returns:
        Representación entera exacta.

    Example:
        >>> _scaled(Decimal("1.25"), 100)
        125
    """
    result = value * scale
    integral = result.to_integral_value()
    if result != integral:
        raise MPLValidationError(
            f"No se pudo representar exactamente el valor {value}."
        )
    return int(integral)


def _array(values: Iterable[int]) -> str:
    """Convierte enteros al formato de arreglo utilizado por DZN.

    Args:
        values: Secuencia de enteros.

    Returns:
        Literal de arreglo MiniZinc.

    Example:
        >>> _array([1, 2, 3])
        '[1, 2, 3]'
    """
    return "[" + ", ".join(str(value) for value in values) + "]"


def instance_to_dzn(instance: MinPolInstance) -> str:
    """Genera el DZN escalado que consume ``Proyecto.mzn``.

    Args:
        instance: Instancia validada que se desea serializar.

    Returns:
        Contenido DZN con costos y opiniones escalados exactamente.

    Example:
        >>> instancia = parse_mpl_text("1\\n1\\n1\\n0.5\\n0\\n0\\n0\\n1")
        >>> "escala_v = 10;" in instance_to_dzn(instancia)
        True
    """

    value_scale = _required_scale(instance.v)
    cost_values = [*instance.ce, instance.ct]
    cost_values.extend(value for row in instance.c for value in row)
    cost_scale = _required_scale(cost_values)

    scaled_v = [_scaled(value, value_scale) for value in instance.v]
    scaled_ce = [_scaled(value, cost_scale) for value in instance.ce]
    scaled_ct = _scaled(instance.ct, cost_scale)
    scaled_c = [
        _scaled(value, cost_scale)
        for row in instance.c
        for value in row
    ]

    source = instance.source.name if instance.source else "contenido en memoria"
    matrix_rows = []
    for row in range(instance.m):
        start = row * instance.m
        values = scaled_c[start : start + instance.m]
        suffix = "," if row < instance.m - 1 else ""
        matrix_rows.append("    " + ", ".join(map(str, values)) + suffix)

    return "\n".join(
        [
            f"% Generado automáticamente desde {source}.",
            "% No editar manualmente: use el conversor MPL.",
            "",
            f"n = {instance.n};",
            f"m = {instance.m};",
            f"p = {_array(instance.p)};",
            "",
            f"escala_v = {value_scale};",
            f"v = {_array(scaled_v)};",
            "",
            f"escala_costo = {cost_scale};",
            f"ce = {_array(scaled_ce)};",
            f"ct = {scaled_ct};",
            f"maxM = {instance.max_movs};",
            "",
            f"c = array2d(1..{instance.m}, 1..{instance.m}, [",
            *matrix_rows,
            "]);",
            "",
        ]
    )


def write_dzn(instance: MinPolInstance, path: str | Path) -> Path:
    """Escribe una instancia validada en formato DZN.

    Args:
        instance: Instancia MinPol validada.
        path: Ruta del archivo que se creará.

    Returns:
        Ruta absoluta del DZN generado.

    Example:
        >>> # write_dzn(instancia, "DatosProyecto.dzn")
    """
    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(instance_to_dzn(instance), encoding="utf-8")
    return destination


def convert_mpl_to_dzn(source: str | Path, destination: str | Path) -> Path:
    """Convierte un archivo MPL a DZN en una sola operación.

    Args:
        source: Ruta del MPL de entrada.
        destination: Ruta del DZN de salida.

    Returns:
        Ruta absoluta del archivo generado.

    Example:
        >>> # convert_mpl_to_dzn("entrada.mpl", "DatosProyecto.dzn")
    """
    return write_dzn(read_mpl(source), destination)


def decimal_text(value: Decimal) -> str:
    """Formatea un decimal sin notación científica.

    Args:
        value: Decimal que se mostrará.

    Returns:
        Representación decimal fija.

    Example:
        >>> decimal_text(Decimal("1.20"))
        '1.20'
    """
    return format(value, "f")
