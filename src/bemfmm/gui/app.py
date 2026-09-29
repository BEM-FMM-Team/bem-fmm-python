import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from bemfmm import softgl


def run(tissue_index=None, setup=None, no_3d=False, mode=None):
    # before the main window imports vtk
    if not no_3d:
        no_3d = not softgl.setup()

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("BEM-FMM")
    app.setOrganizationName("BEM-FMM Team")
    app.setStyle("Fusion")

    from .main_window import MainWindow

    window = MainWindow(tissue_index, setup, no_3d, mode)
    window.show()

    # the run scripts start again without the 3D view when this file is
    # missing after a failed start
    ready_file = os.environ.get("BEMFMM_READY_FILE")
    if ready_file:
        QTimer.singleShot(0, lambda: mark_ready(window, ready_file))

    return app.exec()


def mark_ready(window, path):
    # one render of the shown window first, that is where a broken OpenGL fails
    window.viewport.render()
    Path(path).touch()
