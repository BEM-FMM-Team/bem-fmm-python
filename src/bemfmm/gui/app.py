import sys

from PySide6.QtWidgets import QApplication


def run(tissue_index=None, setup=None, no_3d=False, mode=None):
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("BEM-FMM")
    app.setOrganizationName("WPI")
    app.setStyle("Fusion")

    from .main_window import MainWindow

    window = MainWindow(tissue_index, setup, no_3d, mode)
    window.show()
    return app.exec()
