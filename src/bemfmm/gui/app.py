import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from bemfmm import softgl


def run(tissue_index=None, setup=None, no_3d=False, mode=None, project=None):
    # before anything imports vtk, bemfmm.project does too
    if not no_3d:
        no_3d = not softgl.setup()

    from bemfmm.project import Project

    if project is not None:
        try:
            project = Project.load(project)
        except (OSError, ValueError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 1

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("BEM-FMM")
    app.setOrganizationName("BEM-FMM Team")
    app.setStyle("Fusion")

    from .main_window import MainWindow

    if project is None and not tissue_index and not setup:
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
