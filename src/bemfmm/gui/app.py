import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

STYLE = Path(__file__).resolve().parent / "style.qss"


def run(tissue_index=None, setup=None, no_3d=False):
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("BEM-FMM")
    app.setOrganizationName("WPI")
    app.setStyle("Fusion")
    # the stylesheet is written for the light scheme
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    if STYLE.is_file():
        app.setStyleSheet(STYLE.read_text())

    from .main_window import MainWindow

    window = MainWindow(tissue_index, setup, no_3d)
    window.show()
    return app.exec()
