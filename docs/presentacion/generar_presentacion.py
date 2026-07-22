#!/usr/bin/env python3
"""Genera la presentación MinPol en ODP, PPTX y PDF mediante LibreOffice UNO."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import uno
from com.sun.star.awt import Point, Size
from com.sun.star.beans import PropertyValue

PARA_LEFT = uno.Enum("com.sun.star.style.ParagraphAdjust", "LEFT")
PARA_CENTER = uno.Enum("com.sun.star.style.ParagraphAdjust", "CENTER")
PARA_RIGHT = uno.Enum("com.sun.star.style.ParagraphAdjust", "RIGHT")


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "presentacion"
ASSETS = ROOT / "docs" / "informe" / "assets"

W, H = 33867, 19050  # 16:9, centésimas de milímetro

BG = 0xFAFAF7
BG_2 = 0xF4F5F3
CARD = 0xF0F3F5
CARD_2 = 0xE5EAEE
INK = 0x243746
WHITE = INK  # Nombre histórico: ahora representa el color principal del texto.
ON_DARK = 0xFFFFFF
MUTED = 0x68747D
TEAL = 0x2B5F7A
TEAL_DARK = 0x29485C
AMBER = 0x856A34
BLUE = 0x4F7392
RED = 0x8C4E4E
GREEN = 0x47705D
BORDER = 0xCBD3D9


def prop(name: str, value):
    item = PropertyValue()
    item.Name = name
    item.Value = value
    return item


def connect():
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    last_error = None
    for _ in range(40):
        try:
            ctx = resolver.resolve(
                "uno:pipe,name=minpol_presentacion;urp;StarOffice.ComponentContext"
            )
            smgr = ctx.ServiceManager
            desktop = smgr.createInstanceWithContext(
                "com.sun.star.frame.Desktop", ctx
            )
            return ctx, smgr, desktop
        except Exception as exc:  # LibreOffice puede tardar en iniciar.
            last_error = exc
            time.sleep(0.25)
    raise RuntimeError(
        "No fue posible conectar con LibreOffice mediante la tubería UNO"
    ) from last_error


def clear_page(page):
    while page.getCount():
        page.remove(page.getByIndex(0))


def add_rect(doc, page, x, y, w, h, color, line_color=None, radius=0):
    shape = doc.createInstance("com.sun.star.drawing.RectangleShape")
    shape.Position = Point(x, y)
    shape.Size = Size(w, h)
    shape.FillColor = color
    shape.LineColor = color if line_color is None else line_color
    shape.LineWidth = 0 if line_color is None else 30
    if radius:
        try:
            shape.CornerRadius = min(radius, 60)
        except Exception:
            pass
    page.add(shape)
    return shape


def add_text(
    doc,
    page,
    text,
    x,
    y,
    w,
    h,
    size=20,
    color=WHITE,
    bold=False,
    align="left",
    font="Open Sans",
    margin=70,
):
    shape = doc.createInstance("com.sun.star.drawing.TextShape")
    shape.Position = Point(x, y)
    shape.Size = Size(w, h)
    page.add(shape)
    shape.String = text
    shape.CharFontName = font
    shape.CharHeight = float(size)
    shape.CharColor = color
    shape.CharWeight = 150.0 if bold else 100.0
    shape.ParaAdjust = {
        "left": PARA_LEFT,
        "center": PARA_CENTER,
        "right": PARA_RIGHT,
    }[align]
    shape.TextLeftDistance = margin
    shape.TextRightDistance = margin
    shape.TextUpperDistance = margin
    shape.TextLowerDistance = margin
    return shape


def add_card(doc, page, x, y, w, h, title, body, accent=TEAL, body_size=18):
    add_rect(doc, page, x, y, w, h, CARD, BORDER, radius=40)
    add_rect(doc, page, x, y, 70, h, accent)
    add_text(doc, page, title, x + 360, y + 260, w - 650, 650, 22, accent, True)
    add_text(
        doc,
        page,
        body,
        x + 360,
        y + 980,
        w - 650,
        h - 1190,
        body_size,
        WHITE,
    )


def add_pill(doc, page, text, x, y, w, color=TEAL, text_color=None):
    add_rect(doc, page, x, y, w, 620, BG, color, radius=40)
    add_text(doc, page, text, x + 120, y + 105, w - 240, 380, 13, color if text_color is None else text_color, True, "center", margin=20)


def add_title(doc, page, section, title, subtitle=""):
    add_text(doc, page, section.upper(), 1250, 700, 7200, 520, 13, TEAL, True)
    add_text(doc, page, title, 1180, 1280, 31000, 1120, 29, WHITE, True)
    if subtitle:
        add_text(doc, page, subtitle, 1250, 2420, 30500, 760, 16, MUTED)
    add_rect(doc, page, 1250, 3230, 31000, 20, BORDER)


def add_footer(doc, page, number, speaker, interval, block):
    y = H - 890
    add_text(doc, page, f"{number:02d}", 1180, y, 900, 440, 12, MUTED, True)
    add_text(doc, page, f"{speaker}  ·  {interval}", 2200, y, 12000, 440, 12, MUTED)
    colors = [TEAL, AMBER, BLUE, GREEN]
    x0, total_w = 26900, 5600
    add_rect(doc, page, x0, y + 170, total_w, 60, BORDER)
    add_rect(doc, page, x0, y + 170, total_w * (block + 1) // 4, 60, colors[block])


def add_base(doc, page, number, speaker, interval, block):
    clear_page(page)
    page.Width = W
    page.Height = H
    add_rect(doc, page, 0, 0, W, H, BG)
    add_rect(doc, page, 0, 0, W, 170, INK)
    add_rect(doc, page, 0, 170, W, 55, [TEAL, AMBER, BLUE, GREEN][block])
    add_footer(doc, page, number, speaker, interval, block)


def add_image(doc, page, path: Path, x, y, w, h, white_card=True):
    if white_card:
        add_rect(doc, page, x, y, w, h, 0xFFFFFF, radius=180)
    shape = doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
    shape.GraphicURL = uno.systemPathToFileUrl(str(path.resolve()))
    shape.Position = Point(x + 90, y + 90)
    shape.Size = Size(w - 180, h - 180)
    page.add(shape)
    return shape


def add_arrow(doc, page, x, y, w, color=TEAL):
    line = doc.createInstance("com.sun.star.drawing.LineShape")
    line.Position = Point(x, y)
    line.Size = Size(w, 0)
    line.LineColor = color
    line.LineWidth = 90
    try:
        line.LineEndName = "Arrow"
    except Exception:
        pass
    page.add(line)


def add_metric(doc, page, x, y, w, value, label, color=TEAL):
    add_rect(doc, page, x, y, w, 1850, CARD, BORDER, radius=40)
    add_text(doc, page, value, x + 100, y + 180, w - 200, 760, 26, color, True, "center")
    add_text(doc, page, label, x + 100, y + 1170, w - 200, 430, 13, MUTED, False, "center")


def make_slides(doc):
    pages = doc.getDrawPages()
    while pages.getCount() < 15:
        pages.insertNewByIndex(pages.getCount())
    while pages.getCount() > 15:
        pages.remove(pages.getByIndex(pages.getCount() - 1))

    # 1 — Portada
    p = pages.getByIndex(0)
    add_base(doc, p, 1, "Juan Carlos Cruz Muñoz", "0:00–0:25", 0)
    add_pill(doc, p, "SUSTENTACIÓN · ANÁLISIS DE ALGORITMOS II", 1320, 1250, 14000)
    add_text(doc, p, "Minimizar la\npolarización", 1250, 2750, 20500, 3600, 44, WHITE, True)
    add_text(
        doc,
        p,
        "Un modelo entero lineal para decidir movimientos\nbajo presupuesto y distancia limitada",
        1320,
        6650,
        19500,
        1600,
        21,
        MUTED,
    )
    add_rect(doc, p, 23500, 2400, 7900, 8600, CARD, radius=360)
    add_text(doc, p, "MinPol", 24400, 3200, 6000, 1000, 34, TEAL, True, "center")
    add_text(doc, p, "min", 24200, 5050, 6800, 800, 23, AMBER, True, "center")
    add_text(doc, p, "Σ yᵢ |vᵢ − med(y)|", 24000, 6200, 6900, 1200, 20, WHITE, True, "center")
    add_text(doc, p, "ct  ·  maxM  ·  población", 24450, 8400, 6000, 750, 17, MUTED, False, "center")
    add_text(doc, p, "INTEGRANTES", 1250, 10100, 4500, 500, 13, TEAL, True)
    members = [
        ("Juan Carlos Cruz Muñoz", "1824389"),
        ("David Alejandro Enciso Gutierrez", "2240581"),
        ("Juan Esteban Rodriguez Valencia", "2042282"),
        ("Estiven Andres Martinez Granados", "2179687"),
    ]
    for idx, (name, code) in enumerate(members):
        col, row = idx % 2, idx // 2
        x = 1250 + col * 15550
        y = 10800 + row * 1150
        add_rect(doc, p, x, y, 14750, 900, CARD, radius=160)
        add_rect(doc, p, x, y, 110, 900, TEAL if col == 0 else AMBER)
        add_text(doc, p, f"{name}  ·  {code}", x + 300, y + 190, 14100, 470, 13, WHITE, True, margin=20)
    add_text(doc, p, "Universidad del Valle · Julio de 2026", 1250, 14200, 18000, 650, 14, MUTED, True)

    # 2 — Problema
    p = pages.getByIndex(1)
    add_base(doc, p, 2, "Juan Carlos Cruz Muñoz", "0:25–0:55", 0)
    add_title(doc, p, "1 · Parámetros y variables", "¿Qué problema resolvemos?", "Mover personas solo cuando mejora la distribución y sigue siendo factible")
    stages = [
        ("Estado inicial", "p = personas por opinión", TEAL),
        ("Decisión", "xᵢⱼ = personas de i a j", AMBER),
        ("Estado final", "y = entradas − salidas", BLUE),
        ("Resultado", "mínima polarización", GREEN),
    ]
    x = 1250
    for idx, (title, body, color) in enumerate(stages):
        add_rect(doc, p, x, 4700, 7000, 3600, CARD, radius=260)
        add_text(doc, p, f"0{idx + 1}", x + 350, 5050, 900, 650, 16, color, True)
        add_text(doc, p, title, x + 350, 5850, 6250, 650, 21, WHITE, True)
        add_text(doc, p, body, x + 350, 6800, 6250, 700, 16, MUTED)
        if idx < 3:
            add_arrow(doc, p, x + 7050, 6500, 850, color)
        x += 7950
    add_card(doc, p, 1250, 9500, 14800, 4000, "OBJETIVO", "Minimizar la suma de distancias a la mediana ponderada final.", GREEN, 22)
    add_card(doc, p, 16800, 9500, 14800, 4000, "FACTIBILIDAD", "Presupuesto ct  +  máximo de movimientos maxM  +  conservación.", AMBER, 22)

    # 3 — Parámetros
    p = pages.getByIndex(2)
    add_base(doc, p, 3, "Juan Carlos Cruz Muñoz", "0:55–1:50", 0)
    add_title(doc, p, "1 · Parámetros y variables", "Los datos que describen una instancia", "O = {1,…,m} ·  Σ pᵢ = n ·  0 ≤ vᵢ ≤ 1")
    cards = [
        ("n · m", "Personas totales · opiniones disponibles", TEAL),
        ("pᵢ", "Población inicial en la opinión i", BLUE),
        ("vᵢ", "Valor numérico asociado a i", GREEN),
        ("cᵢⱼ", "Costo base de trasladar i → j", AMBER),
        ("ceⱼ", "Recargo si el destino estaba vacío", RED),
        ("ct", "Presupuesto máximo disponible", AMBER),
        ("maxM", "Distancia total máxima permitida", BLUE),
        ("eⱼ", "1 si pⱼ = 0; 0 en otro caso", TEAL),
    ]
    for idx, (title, body, color) in enumerate(cards):
        col, row = idx % 4, idx // 4
        add_card(doc, p, 1250 + col * 7900, 3950 + row * 4300, 7300, 3600, title, body, color, 16)
    add_rect(doc, p, 1250, 13200, 31000, 1900, CARD_2, radius=220)
    add_text(doc, p, "costo unitario efectivo", 1800, 13650, 6700, 600, 16, MUTED, True)
    add_text(doc, p, "aᵢⱼ = cᵢⱼ (1 + pᵢ / n) + eⱼ · ceⱼ", 8500, 13520, 22000, 800, 25, WHITE, True, "center")

    # 4 — Variables
    p = pages.getByIndex(3)
    add_base(doc, p, 4, "Juan Carlos Cruz Muñoz", "1:50–3:00", 0)
    add_title(doc, p, "1 · Parámetros y variables", "Cuatro familias de variables de decisión", "Todas son enteras o binarias: programación entera lineal (IP/PLE)")
    vars_ = [
        ("xᵢⱼ", "personas que pasan de i a j", TEAL),
        ("yᵢ", "personas finales en i", BLUE),
        ("zₖ", "1 si vₖ es la mediana", AMBER),
        ("qᵢₖ", "producto linealizado yᵢzₖ", GREEN),
    ]
    for idx, (symbol, desc, color) in enumerate(vars_):
        x = 1250 + idx * 7900
        add_rect(doc, p, x, 4000, 7300, 4100, CARD, radius=260)
        add_text(doc, p, symbol, x + 250, 4450, 6800, 1200, 34, color, True, "center")
        add_text(doc, p, desc, x + 350, 6050, 6600, 850, 17, WHITE, False, "center")
    add_card(doc, p, 1250, 9200, 14600, 4200, "EN MINIZINC", "x, y, q ∈ 0..n\nz ∈ 0..1\níndices sobre 1..m", TEAL, 21)
    add_card(doc, p, 16600, 9200, 15650, 4200, "DECIMALES EXACTOS", "v, c, ce y ct llegan como enteros escalados.\nMisma factibilidad; sin ruido binario.", AMBER, 19)

    # 5 — Estructurales
    p = pages.getByIndex(4)
    add_base(doc, p, 5, "David Alejandro Enciso Gutierrez", "3:00–3:45", 1)
    add_title(doc, p, "2 · Restricciones y objetivo", "Primero: que cada movimiento tenga sentido", "Disponibilidad, balance y conservación de la población")
    rows = [
        ("Sin automovimientos", "xᵢᵢ = 0", "Quedarse en i no es mover", TEAL),
        ("Disponibilidad", "Σⱼ≠ᵢ xᵢⱼ ≤ pᵢ", "Nadie se utiliza dos veces", AMBER),
        ("Balance", "yᵢ = pᵢ − salidas + llegadas", "Σᵢ yᵢ = n", BLUE),
    ]
    for idx, (name, formula, note, color) in enumerate(rows):
        y = 3900 + idx * 3500
        add_rect(doc, p, 1250, y, 31000, 2800, CARD, radius=240)
        add_rect(doc, p, 1250, y, 250, 2800, color)
        add_text(doc, p, name, 1850, y + 380, 6500, 580, 20, color, True)
        add_text(doc, p, formula, 8300, y + 480, 14200, 900, 24, WHITE, True, "center")
        add_text(doc, p, note, 23200, y + 400, 7900, 800, 16, MUTED, False, "center")
    add_pill(doc, p, "UNA PERSONA SE MUEVE COMO MÁXIMO UNA VEZ", 9500, 14500, 16000, AMBER)

    # 6 — Recursos
    p = pages.getByIndex(5)
    add_base(doc, p, 6, "David Alejandro Enciso Gutierrez", "3:45–4:30", 1)
    add_title(doc, p, "2 · Restricciones y objetivo", "Dos recursos distintos limitan la solución", "El costo monetario no reemplaza la distancia total recorrida")
    add_card(doc, p, 1250, 4100, 14750, 7200, "PRESUPUESTO", "Σᵢ Σⱼ≠ᵢ aᵢⱼ xᵢⱼ  ≤  ct\n\nIncluye tamaño del grupo de origen\ny recargo del destino vacío.", AMBER, 22)
    add_card(doc, p, 16750, 4100, 15500, 7200, "MOVIMIENTOS", "Σᵢ Σⱼ≠ᵢ |j − i| xᵢⱼ  ≤  maxM\n\nCuenta posiciones recorridas,\nno solo personas trasladadas.", BLUE, 22)
    add_rect(doc, p, 5200, 12400, 23500, 2400, CARD_2, radius=220)
    add_text(doc, p, "Ejemplo", 5750, 12850, 3000, 650, 17, AMBER, True)
    add_text(doc, p, "2 personas de 4 → 1  consumen  2 · |1−4| = 6 movimientos", 8400, 12780, 19300, 850, 21, WHITE, True, "center")

    # 7 — Mediana
    p = pages.getByIndex(6)
    add_base(doc, p, 7, "David Alejandro Enciso Gutierrez", "4:30–5:20", 1)
    add_title(doc, p, "2 · Restricciones y objetivo", "La mediana entra al modelo sin volverlo no lineal", "Una candidata activa; las auxiliares q conectan y con esa candidata")
    add_card(doc, p, 1250, 4050, 9100, 4000, "1 · SELECCIÓN", "Σₖ zₖ = 1\n\nSolo una candidata vₖ queda activa.", AMBER, 20)
    add_card(doc, p, 11350, 4050, 9900, 4000, "2 · LINEALIZACIÓN", "qᵢₖ ≤ yᵢ\nqᵢₖ ≤ nzₖ\nqᵢₖ ≥ yᵢ − n(1−zₖ)", TEAL, 19)
    add_card(doc, p, 22250, 4050, 10000, 4000, "3 · EFECTO", "zₖ = 0  ⇒  qᵢₖ = 0\nzₖ = 1  ⇒  qᵢₖ = yᵢ", GREEN, 20)
    add_rect(doc, p, 1250, 9200, 31000, 3800, CARD_2, radius=260)
    add_text(doc, p, "FUNCIÓN OBJETIVO", 1900, 9650, 6800, 650, 16, GREEN, True)
    add_text(doc, p, "min  P = Σᵢ Σₖ |vᵢ − vₖ| · qᵢₖ", 7600, 10000, 23000, 1000, 30, WHITE, True, "center")
    add_text(doc, p, "Minimizar desviaciones absolutas selecciona una mediana ponderada.", 5600, 11600, 23500, 700, 17, MUTED, False, "center")

    # 8 — Implementación
    p = pages.getByIndex(7)
    add_base(doc, p, 8, "David Alejandro Enciso Gutierrez", "5:20–6:00", 1)
    add_title(doc, p, "2 · Restricciones y objetivo", "De un archivo MPL a un óptimo verificable", "La transformación conserva exactamente los decimales de entrada")
    flow = [
        (".mpl", "entrada", TEAL),
        ("validar", "+ escalar", AMBER),
        (".dzn", "enteros", BLUE),
        ("Proyecto.mzn", "IP/PLE", TEAL),
        ("solver", "ramificación + poda", GREEN),
        ("resultado", "+ 7 checks", AMBER),
    ]
    x = 1100
    for idx, (title, body, color) in enumerate(flow):
        add_rect(doc, p, x, 4500, 4500, 2900, CARD, radius=220)
        title_size = 16 if len(title) > 9 else 20
        add_text(doc, p, title, x + 160, 4920, 4180, 650, title_size, color, True, "center", margin=20)
        add_text(doc, p, body, x + 200, 5950, 4100, 500, 15, MUTED, False, "center")
        if idx < 5:
            add_arrow(doc, p, x + 4520, 5940, 600, color)
        x += 5250
    add_card(doc, p, 1250, 8500, 14600, 4300, "ESCALAMIENTO", "Vᵢ = Sᵥvᵢ  ·  Cᵢⱼ = Sccᵢⱼ\nLa división por n se elimina algebraicamente.", TEAL, 20)
    add_card(doc, p, 16600, 8500, 15650, 4300, "CERTIFICADO DE ÓPTIMO", "Relajación lineal → LB\nIncumbente entero → UB\nLB = UB  ⇒  brecha 0 %", GREEN, 19)

    # 9 — Diseño de pruebas
    p = pages.getByIndex(8)
    add_base(doc, p, 9, "Juan Esteban Rodriguez Valencia", "6:00–6:35", 2)
    add_title(doc, p, "3 · Resultados y análisis", "La solución se comprueba desde varias capas", "El verificador independiente no confía en las etiquetas del solver")
    metrics = [
        ("6", "instancias principales", TEAL),
        ("4", "variaciones controladas", AMBER),
        ("30", "entradas suministradas", BLUE),
        ("100 %", "con estado óptimo", GREEN),
    ]
    for idx, item in enumerate(metrics):
        add_metric(doc, p, 1250 + idx * 7900, 3900, 7300, *item)
    checks = [
        "dominio y diagonal",
        "disponibilidad por origen",
        "balance y conservación",
        "costo y presupuesto",
        "distancia ≤ maxM",
        "mediana y polarización",
    ]
    add_rect(doc, p, 1250, 6700, 31000, 6600, CARD, radius=280)
    add_text(doc, p, "VERIFICACIÓN INDEPENDIENTE", 1900, 7200, 10000, 650, 18, BLUE, True)
    for idx, check in enumerate(checks):
        col, row = idx % 2, idx // 2
        x = 1900 + col * 15000
        y = 8400 + row * 1300
        add_text(doc, p, "OK", x, y, 1300, 600, 14, GREEN, True, "center", margin=20)
        add_text(doc, p, check, x + 1450, y, 12050, 600, 17, WHITE)
    add_pill(doc, p, "10 PRUEBAS DE INTEGRACIÓN · 8 UNITARIAS", 9000, 14100, 16500, BLUE)

    # 10 — Tabla resultados
    p = pages.getByIndex(9)
    add_base(doc, p, 10, "Juan Esteban Rodriguez Valencia", "6:35–7:20", 2)
    add_title(doc, p, "3 · Resultados y análisis", "Seis instancias, seis óptimos certificados", "MiniZinc 2.9.7 · HiGHS 1.14.0 · tiempos puntuales del solver")
    headers = ["Instancia", "n", "m", "Costo", "Movs.", "Pol.", "s", "Nodos"]
    widths = [8200, 2500, 2500, 4200, 3500, 3300, 3500, 3300]
    x0, y0, row_h = 1250, 3900, 1550
    x = x0
    for text_, width in zip(headers, widths):
        add_rect(doc, p, x, y0, width, row_h, TEAL_DARK)
        add_text(doc, p, text_, x + 60, y0 + 420, width - 120, 550, 15, ON_DARK, True, "center")
        x += width
    data = [
        ("Ejemplo PDF", "20", "5", "19.2", "14", "0.5", "0.0255", "1"),
        ("Consenso", "10", "4", "11.7", "6", "0", "0.0121", "1"),
        ("Presupuesto bajo", "20", "5", "9.8", "7", "5.8", "0.1048", "9"),
        ("Costo extra alto", "24", "6", "30", "18", "6.75", "0.1867", "11"),
        ("Decimales", "18", "6", "18.6667", "14", "2.75", "0.2588", "76"),
        ("Instancia grande", "40", "8", "44.85", "24", "11.7", "0.3547", "15"),
    ]
    for r_idx, row in enumerate(data):
        y = y0 + (r_idx + 1) * row_h
        x = x0
        fill = CARD if r_idx % 2 == 0 else CARD_2
        for c_idx, (text_, width) in enumerate(zip(row, widths)):
            add_rect(doc, p, x, y, width, row_h, fill, CARD_2)
            color = GREEN if c_idx == 5 and text_ == "0" else WHITE
            align = "left" if c_idx == 0 else "center"
            add_text(doc, p, text_, x + 100, y + 390, width - 200, 580, 15, color, c_idx in (0, 5), align)
            x += width
    add_text(doc, p, "30/30 entradas suministradas: óptimas y verificadas · 23 coincidencias textuales · 7 diferencias de 0.001", 1500, 14800, 30000, 700, 16, MUTED, True, "center")

    # 11 — Sensibilidad
    p = pages.getByIndex(10)
    add_base(doc, p, 11, "Juan Esteban Rodriguez Valencia", "7:20–8:10", 2)
    add_title(doc, p, "3 · Resultados y análisis", "Presupuesto y recargos cambian el óptimo", "Las comparaciones aíslan un parámetro y mantienen los demás fijos")
    add_image(doc, p, ASSETS / "presupuesto_polarizacion.png", 1250, 3900, 15000, 8400)
    add_image(doc, p, ASSETS / "impacto_costo_extra.png", 17000, 3900, 15250, 8400)
    add_pill(doc, p, "ct: 0 → 24  ·  polarización: 4 → 0", 2900, 13200, 12000, TEAL)
    add_pill(doc, p, "ce: 12 → 0  ·  polarización: 6.75 → 6", 18100, 13200, 13200, AMBER)

    # 12 — Eficiencia / B&B
    p = pages.getByIndex(11)
    add_base(doc, p, 12, "Juan Esteban Rodriguez Valencia", "8:10–9:00", 2)
    add_title(doc, p, "3 · Resultados y análisis", "Branch and Bound: ramificar, acotar y podar", "Tamaño: m² variables x + m² auxiliares q + m binarias z")
    add_image(doc, p, ASSETS / "nodos_instancias.png", 1250, 3900, 15200, 8800)
    add_card(doc, p, 17300, 3900, 14950, 2100, "RAMIFICACIÓN", "Variable fraccionaria → dos subproblemas.", BLUE, 14)
    add_card(doc, p, 17300, 6150, 14950, 2100, "PODA INFACTIBLE", "La relajación lineal no tiene solución.", RED, 14)
    add_card(doc, p, 17300, 8400, 14950, 2100, "PODA POR COTA", "En minimización, LB ≥ UB: no mejora al incumbente.", AMBER, 14)
    add_card(doc, p, 17300, 10650, 14950, 2100, "CIERRE INTEGRAL", "Si una solución entera mejora, actualiza el incumbente y UB.", GREEN, 13)
    add_rect(doc, p, 17300, 13100, 14950, 1650, CARD_2, radius=200)
    add_text(doc, p, "HiGHS: 1 nodo · Chuffed: 225 nodos", 17750, 13380, 14000, 520, 17, WHITE, True, "center")
    add_text(doc, p, "Misma instancia; estrategias distintas", 17750, 14000, 14000, 420, 13, MUTED, False, "center")

    # 13 — Prueba ejemplo
    p = pages.getByIndex(12)
    add_base(doc, p, 13, "Estiven Andres Martinez Granados", "9:00–10:15", 3)
    add_title(doc, p, "4 · Pruebas y conclusiones", "Prueba 1 · ejemplo del enunciado", "Cargar MPL · generar DZN · resolver con HiGHS · revisar 7 verificaciones")
    add_pill(doc, p, "INICIAL  [12, 4, 0, 4, 0]", 1250, 3650, 8800, BLUE)
    add_arrow(doc, p, 10500, 3950, 2600, AMBER)
    add_pill(doc, p, "FINAL  [18, 2, 0, 0, 0]", 13600, 3650, 9800, GREEN)
    add_text(doc, p, "4× (2→1)  ·  2× (4→1)  ·  2× (4→2)", 5000, 5300, 23500, 700, 22, WHITE, True, "center")
    metrics = [
        ("19.2 / 20", "costo", AMBER),
        ("14 / 18", "movimientos", BLUE),
        ("0", "mediana", TEAL),
        ("0.5", "polarización", GREEN),
    ]
    for idx, item in enumerate(metrics):
        add_metric(doc, p, 1250 + idx * 7900, 6900, 7300, *item)
    add_card(doc, p, 1250, 9300, 14900, 3600, "COMPROBACIÓN", "Costo: 4.8 + 9.6 + 4.8 = 19.2\nMovs.: 4 + 6 + 4 = 14", TEAL, 19)
    add_card(doc, p, 16900, 9300, 15350, 3600, "MEJORA CERTIFICADA", "Polarización 4 → 0.5  (−87.5 %)\n447 distribuciones factibles enumeradas", GREEN, 19)
    add_pill(doc, p, "DOMINIO · BALANCE · PRESUPUESTO · maxM · MEDIANA", 5700, 13900, 22400, GREEN)

    # 14 — Prueba consenso
    p = pages.getByIndex(13)
    add_base(doc, p, 14, "Estiven Andres Martinez Granados", "10:15–11:05", 3)
    add_title(doc, p, "4 · Pruebas y conclusiones", "Prueba 2 · consenso alcanzable", "Tres personas recorren dos posiciones y consumen todo maxM")
    add_pill(doc, p, "INICIAL  [7, 0, 3, 0]", 1250, 3650, 8200, BLUE)
    add_arrow(doc, p, 10100, 3950, 2800, AMBER)
    add_pill(doc, p, "FINAL  [10, 0, 0, 0]", 13500, 3650, 9000, GREEN)
    add_rect(doc, p, 23800, 3400, 8450, 1150, CARD, radius=220)
    add_text(doc, p, "3 personas · 3 → 1", 24100, 3690, 7850, 560, 18, WHITE, True, "center")
    add_card(doc, p, 1250, 5900, 9800, 4700, "PRESUPUESTO", "3 × costo efectivo\n= 11.7 ≤ 12", AMBER, 22)
    add_card(doc, p, 12000, 5900, 9800, 4700, "DISTANCIA", "3 × |1−3|\n= 6 = maxM", BLUE, 22)
    add_card(doc, p, 22750, 5900, 9500, 4700, "OBJETIVO", "10 × |0−0|\n= 0", GREEN, 22)
    add_rect(doc, p, 1250, 11800, 31000, 2400, CARD_2, radius=240)
    add_text(doc, p, "CONSENSO", 2300, 12300, 5600, 700, 22, GREEN, True)
    add_text(doc, p, "Es posible solo si una concentración completa respeta ct y maxM simultáneamente.", 7700, 12250, 23400, 800, 19, WHITE, True, "center")

    # 15 — Conclusiones
    p = pages.getByIndex(14)
    add_base(doc, p, 15, "Estiven Andres Martinez Granados", "11:05–12:00", 3)
    add_title(doc, p, "4 · Pruebas y conclusiones", "Qué demostramos", "Movimientos factibles, auditables y óptimos para las instancias evaluadas")
    conclusions = [
        ("01", "Modelo exacto", "IP/PLE con mediana linealizada", TEAL),
        ("02", "Factibilidad", "Población, ct y maxM separados", AMBER),
        ("03", "Precisión", "Escalamiento entero de decimales", BLUE),
        ("04", "Evidencia", "30/30 entradas verificadas", GREEN),
        ("05", "Límite", "Crecimiento cuadrático en m", RED),
    ]
    for idx, (num, title, body, color) in enumerate(conclusions):
        col = idx % 3
        row = idx // 3
        x = 1250 + col * 10400
        y = 3900 + row * 3900
        w = 9700 if idx < 3 else 14950
        if idx >= 3:
            x = 1250 + (idx - 3) * 15550
        add_rect(doc, p, x, y, w, 3300, CARD, radius=240)
        add_text(doc, p, num, x + 300, y + 300, 1400, 650, 17, color, True)
        add_text(doc, p, title, x + 1750, y + 300, w - 2100, 650, 20, WHITE, True)
        add_text(doc, p, body, x + 350, y + 1450, w - 700, 800, 16, MUTED, False, "center")
    add_rect(doc, p, 1250, 12300, 30500, 2300, TEAL_DARK, radius=300)
    add_text(doc, p, "MinPol", 1850, 12700, 4500, 850, 27, ON_DARK, True)
    add_text(doc, p, "Brecha 0 %  ·  verificación independiente  ·  resultados reproducibles", 6100, 12750, 24300, 700, 19, ON_DARK, True, "center")
    add_text(doc, p, "Muchas gracias", 1250, 15000, 30500, 850, 23, GREEN, True, "center")


def save(doc):
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = [
        (OUT / "Presentacion_MinPol.odp", "impress8"),
        (OUT / "Presentacion_MinPol.pptx", "Impress MS PowerPoint 2007 XML"),
    ]
    odp_url = uno.systemPathToFileUrl(str(outputs[0][0]))
    doc.storeAsURL(odp_url, (prop("FilterName", outputs[0][1]), prop("Overwrite", True)))
    for path, filter_name in outputs[1:]:
        doc.storeToURL(
            uno.systemPathToFileUrl(str(path)),
            (prop("FilterName", filter_name), prop("Overwrite", True)),
        )


def main():
    _, _, desktop = connect()
    doc = desktop.loadComponentFromURL("private:factory/simpress", "_blank", 0, ())
    try:
        make_slides(doc)
        save(doc)
    finally:
        doc.close(True)
    print("Presentación generada en", OUT)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
