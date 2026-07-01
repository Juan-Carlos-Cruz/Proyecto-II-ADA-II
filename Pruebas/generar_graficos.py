#!/usr/bin/env python3
"""Genera con Pillow las figuras usadas en el análisis experimental."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "informe" / "assets"
OUTPUT.mkdir(parents=True, exist_ok=True)
FONT_PATH = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"


def font(size: int, bold: bool = False):
    """Carga una fuente disponible para los gráficos.

    Args:
        size: Tamaño tipográfico en puntos.
        bold: Solicita una variante destacada.

    Returns:
        Fuente compatible con Pillow.

    Example:
        >>> fuente = font(18)
        >>> fuente is not None
        True
    """
    path = FONT_PATH
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, style) -> None:
    """Dibuja texto centrado horizontalmente.

    Args:
        draw: Contexto de dibujo de Pillow.
        xy: Centro horizontal y posición vertical.
        text: Contenido que se dibujará.
        style: Fuente de Pillow.

    Returns:
        None.

    Example:
        >>> # centered(dibujo, (100, 20), "Título", fuente)
    """
    box = draw.textbbox((0, 0), text, font=style)
    width = box[2] - box[0]
    draw.text((xy[0] - width / 2, xy[1]), text, fill="#222222", font=style)


def canvas(title: str, y_label: str):
    """Crea el lienzo base de una gráfica.

    Args:
        title: Título principal.
        y_label: Etiqueta del eje vertical.

    Returns:
        Tupla con imagen y contexto de dibujo.

    Example:
        >>> imagen, dibujo = canvas("Prueba", "Valor")
        >>> imagen.size
        (1200, 700)
    """
    image = Image.new("RGB", (1200, 700), "white")
    draw = ImageDraw.Draw(image)
    centered(draw, (600, 25), title, font(34, bold=True))
    draw.text((25, 80), y_label, fill="#222222", font=font(24))
    draw.line((130, 100, 130, 590), fill="#333333", width=3)
    draw.line((130, 590, 1130, 590), fill="#333333", width=3)
    return image, draw


def budget_chart() -> None:
    """Genera la gráfica de presupuesto frente a polarización.

    Returns:
        None.

    Example:
        >>> # budget_chart()
    """
    budgets = [0, 10, 20, 24]
    values = [4, 2, 0.5, 0]
    image, draw = canvas(
        "Efecto del presupuesto en el ejemplo del PDF",
        "Polarización óptima",
    )
    points = []
    for budget, value in zip(budgets, values):
        x = 150 + budget / 24 * 940
        y = 560 - value / 4 * 420
        points.append((x, y))
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill="#4472C4")
        centered(draw, (int(x), int(y - 42)), str(value), font(22, bold=True))
        centered(draw, (int(x), 605), str(budget), font(22))
    draw.line(points, fill="#4472C4", width=6)
    centered(draw, (620, 650), "Presupuesto ct", font(24))
    image.save(OUTPUT / "presupuesto_polarizacion.png")


def bar_chart(
    filename: str,
    title: str,
    y_label: str,
    labels: list[str],
    values: list[float],
    colors: list[str],
) -> None:
    """Genera una gráfica de barras reutilizable.

    Args:
        filename: Nombre del PNG de salida.
        title: Título de la gráfica.
        y_label: Etiqueta del eje vertical.
        labels: Etiquetas de las barras.
        values: Alturas numéricas.
        colors: Colores que se alternarán.

    Returns:
        None.

    Example:
        >>> # bar_chart("x.png", "Título", "Valor", ["A"], [1], ["#000"])
    """
    image, draw = canvas(title, y_label)
    maximum = max(values) * 1.15
    available = 900
    bar_width = min(140, int(available / max(1, len(values)) * 0.55))
    spacing = available / len(values)
    for index, (label, value) in enumerate(zip(labels, values)):
        center_x = 170 + spacing * (index + 0.5)
        top = 560 - value / maximum * 420
        draw.rectangle(
            (center_x - bar_width / 2, top, center_x + bar_width / 2, 590),
            fill=colors[index % len(colors)],
        )
        centered(draw, (int(center_x), int(top - 38)), str(value), font(22, bold=True))
        centered(draw, (int(center_x), 610), label, font(20))
    image.save(OUTPUT / filename)


def node_chart() -> None:
    """Genera la comparación de nodos entre instancias.

    Returns:
        None.

    Example:
        >>> # node_chart()
    """
    bar_chart(
        "nodos_instancias.png",
        "Nodos de Branch and Bound por instancia",
        "Nodos HiGHS",
        ["I1 m=4", "I2 m=5", "I3 m=6", "I4 m=6", "I5 m=8"],
        [1, 3, 11, 72, 51],
        ["#4472C4"],
    )


def extra_cost_chart() -> None:
    """Genera la comparación experimental de costos extra.

    Returns:
        None.

    Example:
        >>> # extra_cost_chart()
    """
    bar_chart(
        "impacto_costo_extra.png",
        "Influencia del costo extra",
        "Polarización óptima",
        ["ce central=12", "ce=0"],
        [6.75, 4.8],
        ["#C55A11", "#70AD47"],
    )


if __name__ == "__main__":
    budget_chart()
    node_chart()
    extra_cost_chart()
    print(f"Gráficos generados en {OUTPUT}")
