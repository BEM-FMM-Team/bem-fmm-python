import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from bemfmm import softgl


def run(tissue_index=None, setup=None, no_3d=False, mode=None, project=None):
    # before the main window imports vtk
    if not no_3d:
        no_3d = not softgl.setup()

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("BEM-FMM")
    app.setOrganizationName("BEM-FMM Team")
    app.setStyle("Fusion")

    from bemfmm.project import Project

    from .main_window import MainWindow

    if project is not None:
        project = Project.load(project)
    elif not tissue_index and not setup:
        project = ask_project()
    window = MainWindow(tissue_index, setup, no_3d, mode, project)
    window.show()

    # the run scripts start again without the 3D view when this file is
    # missing after a failed start
    ready_file = os.environ.get("BEMFMM_READY_FILE")
    if ready_file:
        QTimer.singleShot(0, lambda: mark_ready(window, ready_file))

    return app.exec()


def ask_project():
    # the project to start with, None for the last one
    from .dialogs import ProjectDialog
    from .settings import Settings

    settings = Settings()
    if not settings["ask_project"]:
        return None
    dialog = ProjectDialog(settings)
    return dialog.project if dialog.exec() else None


def mark_ready(window, path):
    # one render of the shown window first, that is where a broken OpenGL fails
    window.viewport.render()
    Path(path).touch()
