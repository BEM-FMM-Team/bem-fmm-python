from pathlib import Path
from string import Template

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QPalette

"""
Light and dark themes. style.qss is a template, the $names in it are filled
from COLORS so both themes share one stylesheet
"""

STYLE = Path(__file__).resolve().parent / "style.qss"

THEMES = ["system", "light", "dark"]

COLORS = {
    "light": {
        "window": "#f4f6f7",
        "panel": "#ffffff",
        "base": "#ffffff",
        "text": "#1c2226",
        "muted": "#56626b",
        "tab": "#4a5760",
        "title": "#33404a",
        "border": "#d5dbdf",
        "trough": "#eef1f3",
        "log": "#fbfbfb",
        "accent": "#1f4f8f",
        "accent_text": "#1f4f8f",
        "accent_hover": "#173f73",
        "accent_disabled": "#9fb0c8",
        "accent_soft": "#dbe6f5",
    },
    "dark": {
        "window": "#1b1f23",
        "panel": "#23282d",
        "base": "#181b1f",
        "text": "#e1e5e8",
        "muted": "#98a3ab",
        "tab": "#a4afb7",
        "title": "#c6ced4",
        "border": "#363d44",
        "trough": "#2a3036",
        "log": "#15181b",
        "accent": "#3d6fb3",
        "accent_text": "#8db4ea",
        "accent_hover": "#4a7dc2",
        "accent_disabled": "#34465e",
        "accent_soft": "#263a55",
    },
}


def resolve(theme):
    # system becomes light or dark, whatever the desktop uses
    if theme in ("light", "dark"):
        return theme
    hints = QGuiApplication.styleHints()
    hints.unsetColorScheme()
    return "dark" if hints.colorScheme() == Qt.ColorScheme.Dark else "light"


def dark_palette():
    c = COLORS["dark"]
    palette = QPalette()
    for role, color in (
        (QPalette.Window, c["window"]),
        (QPalette.WindowText, c["text"]),
        (QPalette.Base, c["base"]),
        (QPalette.AlternateBase, c["panel"]),
        (QPalette.ToolTipBase, c["panel"]),
        (QPalette.ToolTipText, c["text"]),
        (QPalette.PlaceholderText, c["muted"]),
        (QPalette.Text, c["text"]),
        (QPalette.Button, "#2c3238"),
        (QPalette.ButtonText, c["text"]),
        (QPalette.BrightText, "#ff6b6b"),
        (QPalette.Light, "#3a4148"),
        (QPalette.Midlight, "#30363c"),
        (QPalette.Mid, "#24292e"),
        (QPalette.Dark, "#121518"),
        (QPalette.Shadow, "#000000"),
        (QPalette.Highlight, c["accent"]),
        (QPalette.HighlightedText, "#ffffff"),
        (QPalette.Link, c["accent_text"]),
    ):
        palette.setColor(role, QColor(color))
    for role in (QPalette.Text, QPalette.ButtonText, QPalette.WindowText):
        palette.setColor(QPalette.Disabled, role, QColor("#687279"))
    palette.setColor(QPalette.Disabled, QPalette.Base, QColor(c["window"]))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor("#262b30"))
    return palette


def apply(app, theme):
    """
    Sets the palette and stylesheet of the application, returns the theme that
    was applied, light or dark
    """
    name = resolve(theme)
    if theme != "system":
        scheme = Qt.ColorScheme.Dark if name == "dark" else Qt.ColorScheme.Light
        app.styleHints().setColorScheme(scheme)
    if name == "dark":
        app.setPalette(dark_palette())
    else:
        app.setPalette(app.style().standardPalette())
    if STYLE.is_file():
        app.setStyleSheet(Template(STYLE.read_text()).substitute(COLORS[name]))
    return name


def plot_style(name):
    # matplotlib rc for figures embedded in the window
    c = COLORS[name]
    return {
        "figure.facecolor": c["panel"],
        "axes.facecolor": c["base"],
        "axes.edgecolor": c["muted"],
        "axes.labelcolor": c["text"],
        "axes.titlecolor": c["text"],
        "text.color": c["text"],
        "xtick.color": c["muted"],
        "ytick.color": c["muted"],
        "xtick.labelcolor": c["text"],
        "ytick.labelcolor": c["text"],
        "grid.color": c["border"],
        "legend.facecolor": c["panel"],
        "legend.edgecolor": c["border"],
        "legend.labelcolor": c["text"],
        "savefig.facecolor": "auto",
    }
