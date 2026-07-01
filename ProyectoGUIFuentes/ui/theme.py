"""Paleta y estilos ttk compartidos por todas las vistas."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


COLORS = {
    "background": "#f3f5f8",
    "surface": "#ffffff",
    "sidebar": "#172033",
    "sidebar_soft": "#23304a",
    "primary": "#2563eb",
    "primary_dark": "#1d4ed8",
    "success": "#059669",
    "text": "#172033",
    "muted": "#64748b",
    "border": "#dbe2ea",
    "chart": "#3b82f6",
}


def configure_styles(root: tk.Misc) -> None:
    """Registra la paleta y los estilos ttk de la aplicación.

    Args:
        root: Intérprete Tk donde se registrarán los estilos.

    Returns:
        None.

    Example:
        >>> # configure_styles(root)
    """
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        ".",
        font=("TkDefaultFont", 10),
        background=COLORS["background"],
        foreground=COLORS["text"],
    )
    style.configure("App.TFrame", background=COLORS["background"])
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure(
        "CompliancePanel.TFrame",
        background="#ecfdf5",
        bordercolor="#a7f3d0",
        borderwidth=1,
        relief="solid",
    )
    style.configure("Compliance.TFrame", background="#ecfdf5")
    style.configure("Sidebar.TFrame", background=COLORS["sidebar"])
    style.configure(
        "Sidebar.TLabel",
        background=COLORS["sidebar"],
        foreground="#ffffff",
    )
    style.configure(
        "SidebarMuted.TLabel",
        background=COLORS["sidebar"],
        foreground="#b8c4d8",
    )
    style.configure(
        "Title.TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=("TkDefaultFont", 20, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["background"],
        foreground=COLORS["muted"],
    )
    style.configure(
        "Section.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("TkDefaultFont", 11, "bold"),
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["muted"],
    )
    style.configure(
        "ComplianceTitle.TLabel",
        background="#ecfdf5",
        foreground="#065f46",
        font=("TkDefaultFont", 10, "bold"),
    )
    style.configure(
        "ComplianceSummary.TLabel",
        background="#ecfdf5",
        foreground=COLORS["success"],
        font=("TkDefaultFont", 9, "bold"),
    )
    style.configure(
        "ComplianceItem.TLabel",
        background="#ecfdf5",
        foreground=COLORS["text"],
        font=("TkDefaultFont", 8),
    )
    style.configure(
        "CompliancePending.TLabel",
        background="#ecfdf5",
        foreground=COLORS["success"],
        font=("TkDefaultFont", 10, "bold"),
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground="#ffffff",
        padding=(14, 10),
        borderwidth=0,
    )
    style.map(
        "Primary.TButton",
        background=[
            ("active", COLORS["primary_dark"]),
            ("disabled", "#9db7ee"),
        ],
        foreground=[("disabled", "#eef3ff")],
    )
    style.configure(
        "Secondary.TButton",
        background=COLORS["sidebar_soft"],
        foreground="#ffffff",
        padding=(14, 9),
        borderwidth=0,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#30405f"), ("disabled", "#34405a")],
        foreground=[("disabled", "#8f9bb0")],
    )
    style.configure(
        "Outline.TButton",
        background=COLORS["surface"],
        foreground=COLORS["primary"],
        padding=(12, 8),
        bordercolor=COLORS["primary"],
        borderwidth=1,
    )
    style.map(
        "Outline.TButton",
        background=[("active", "#eff6ff")],
        foreground=[("active", COLORS["primary_dark"])],
    )
    style.configure(
        "Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=28,
        bordercolor=COLORS["border"],
        borderwidth=1,
    )
    style.configure(
        "Treeview.Heading",
        background="#e9eef5",
        foreground=COLORS["text"],
        font=("TkDefaultFont", 9, "bold"),
        padding=(8, 7),
    )
    style.map(
        "Treeview",
        background=[("selected", "#dbeafe")],
        foreground=[("selected", COLORS["text"])],
    )
    style.configure("TNotebook", background=COLORS["background"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        padding=(16, 9),
        font=("TkDefaultFont", 10, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["surface"])],
        foreground=[("selected", COLORS["primary"])],
    )
    style.configure(
        "Status.TLabel",
        background="#e8eef7",
        foreground=COLORS["text"],
        padding=(12, 7),
    )
    style.configure(
        "Horizontal.TProgressbar",
        background=COLORS["primary"],
        troughcolor=COLORS["sidebar_soft"],
        borderwidth=0,
    )
