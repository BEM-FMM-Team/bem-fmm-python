from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QListWidgetItem,
    QMessageBox,
    QSpinBox,
)

from bemfmm.coils import CHOICES, COIL_LABELS, COIL_PARAMS, param_info
from bemfmm.project import Project, default_project, new_project, sphere_project
from bemfmm.results import FIELD_LABELS

from .settings import START_MODES, Settings
from .theme import THEMES
from .ui_coil_params import Ui_CoilParamsDialog
from .ui_export_dialog import Ui_ExportDialog
from .ui_project_dialog import Ui_ProjectDialog
from .ui_settings_dialog import Ui_SettingsDialog

MESH_FILTER = "Surface mesh (*.stl *.obj *.ply *.vtk);;All Files (*)"


def empty_folder(parent, title):
    # a folder picked for something new, None when cancelled or not empty
    folder = QFileDialog.getExistingDirectory(parent, title)
    if not folder:
        return None
    folder = Path(folder)
    if any(folder.iterdir()):
        QMessageBox.warning(parent, title, f"{folder} is not empty.")
        return None
    return folder


def last_project(settings):
    # the project opened last, the default head when it is gone or broken
    folder = settings["project"]
    if folder:
        try:
            project = Project.load(folder)
            if not project.problems():
                return project
        except (OSError, ValueError):
            pass
    return default_project()


def open_project_folder(parent):
    """A project picked with a folder dialog, None when cancelled or bad"""
    folder = QFileDialog.getExistingDirectory(parent, "Open project")
    if not folder:
        return None
    try:
        project = Project.load(folder)
    except (OSError, ValueError) as error:
        QMessageBox.warning(parent, "Open project", str(error))
        return None
    problems = project.problems()
    if problems:
        QMessageBox.warning(parent, "Open project", "\n".join(problems))
        return None
    return project


def new_project_from_surfaces(parent):
    """
    Asks for the surfaces and an empty folder and makes a project there. The
    project, or None when cancelled or it failed
    """
    meshes, _ = QFileDialog.getOpenFileNames(
        parent, "Surfaces of the new project, in mm", "", MESH_FILTER
    )
    if not meshes:
        return None
    folder = empty_folder(parent, "Folder for the new project")
    if folder is None:
        return None
    try:
        project, problems = new_project(folder, meshes)
    except (OSError, ValueError) as error:
        QMessageBox.warning(parent, "New project", str(error))
        return None
    if problems:
        QMessageBox.warning(
            parent,
            "New project",
            "The project was made, but the surfaces have problems. Fix them, "
            "or the tissues in the Model tab, before solving:\n\n"
            + "\n".join(problems),
        )
    return project


class ProjectDialog(QDialog):
    """
    Picks the project to open: the bundled ones, the recent ones, a folder or
    a new one from surfaces
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.ui = Ui_ProjectDialog()
        self.ui.setupUi(self)
        self.settings = settings
        self.project = None
        ui = self.ui

        projects = [default_project(), sphere_project()]
        for folder in settings.recent_projects():
            try:
                project = Project.load(folder)
            except (OSError, ValueError):
                continue
            if project.root not in [p.root for p in projects]:
                projects.append(project)
        last = settings["project"]
        for project in projects:
            text = f"{project.name}   {project.root}"
            if project.read_only:
                text = f"{project.name} (read only)   {project.root}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, project)
            ui.projectList.addItem(item)
            if last and Path(last).resolve() == project.root:
                ui.projectList.setCurrentItem(item)
        if ui.projectList.currentRow() < 0:
            ui.projectList.setCurrentRow(0)

        ui.askCheck.setChecked(settings["ask_project"])
        ui.projectList.itemDoubleClicked.connect(self.accept)
        ui.openFolderButton.clicked.connect(
            lambda: self.done_with(open_project_folder(self))
        )
        ui.newProjectButton.clicked.connect(
            lambda: self.done_with(new_project_from_surfaces(self))
        )

    def done_with(self, project):
        if project is not None:
            self.project = project
            super().accept()

    def accept(self):
        item = self.ui.projectList.currentItem()
        if item is None:
            return
        self.project = item.data(Qt.UserRole)
        super().accept()

    def done(self, result):
        self.settings["ask_project"] = self.ui.askCheck.isChecked()
        super().done(result)


class CoilParamsDialog(QDialog):
    """
    Generator parameters for a new coil, one row per parameter
    """

    def __init__(self, coil_type, parent=None):
        super().__init__(parent)
        self.ui = Ui_CoilParamsDialog()
        self.ui.setupUi(self)
        self.setWindowTitle(f"{COIL_LABELS.get(coil_type, coil_type)} parameters")

        self.params = COIL_PARAMS[coil_type]
        self.entries = {}
        self.scales = {}  # lengths are stored in m and shown in mm
        for name, info in self.params.items():
            label, unit, tip = param_info(coil_type, name)
            self.scales[name] = 1000.0 if unit.startswith("mm") else 1.0
            if name in CHOICES:
                widget = QComboBox()
                for value, text in CHOICES[name].items():
                    widget.addItem(text, value)
            elif info["type"] is int:
                widget = QSpinBox()
                widget.setRange(1, 100000)
            else:
                widget = QDoubleSpinBox()
                widget.setDecimals(3)
                widget.setRange(-1000.0, 1000.0)
                widget.setSingleStep(0.1 if unit else 1.0)
                if unit:
                    widget.setSuffix(f" {unit}")
            widget.setToolTip(tip)
            self.entries[name] = widget
            self.ui.form.addRow(label, widget)
            self.ui.form.labelForField(widget).setToolTip(tip)

        self.restore_defaults()
        self.ui.buttonBox.button(
            QDialogButtonBox.StandardButton.RestoreDefaults
        ).clicked.connect(self.restore_defaults)

    def restore_defaults(self):
        for name, widget in self.entries.items():
            default = self.params[name]["default"]
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(widget.findData(default))
            else:
                widget.setValue(default * self.scales[name])

    def values(self):
        values = {}
        for name, widget in self.entries.items():
            default = self.params[name]["default"]
            if isinstance(widget, QComboBox):
                values[name] = widget.currentData()
            elif isinstance(widget, QSpinBox):
                values[name] = widget.value()
            elif widget.value() == round(default * self.scales[name], 3):
                # unchanged, the default exactly and not the mm round trip
                values[name] = default
            else:
                values[name] = widget.value() / self.scales[name]
        return values


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.settings = settings
        self.ui.outputEdit.setPlaceholderText("__output__ in the working folder")

        self.ui.browseButton.clicked.connect(self.browse)
        self.ui.buttonBox.button(
            QDialogButtonBox.StandardButton.RestoreDefaults
        ).clicked.connect(lambda: self.fill(Settings.DEFAULTS))
        self.fill({key: settings[key] for key in Settings.DEFAULTS})

    def fill(self, values):
        ui = self.ui
        theme, start = values["theme"], values["start_mode"]
        ui.themeCombo.setCurrentIndex(THEMES.index(theme) if theme in THEMES else 0)
        ui.skinEdit.setText(values["skin"])
        ui.startModeCombo.setCurrentIndex(
            START_MODES.index(start) if start in START_MODES else 0
        )
        ui.outputEdit.setText(values["output_dir"])
        ui.slicesCheck.setChecked(values["slices"])

    def browse(self):
        path = QFileDialog.getExistingDirectory(
            self, "Output folder", self.ui.outputEdit.text()
        )
        if path:
            self.ui.outputEdit.setText(path)

    def accept(self):
        ui = self.ui
        self.settings["theme"] = THEMES[ui.themeCombo.currentIndex()]
        self.settings["skin"] = ui.skinEdit.text().strip() or "skin"
        self.settings["start_mode"] = START_MODES[ui.startModeCombo.currentIndex()]
        self.settings["output_dir"] = ui.outputEdit.text().strip()
        self.settings["slices"] = ui.slicesCheck.isChecked()
        super().accept()


class ExportDialog(QDialog):
    """
    Picks the fields, facets, format and folder to export a result to
    """

    def __init__(self, result, folder, parent=None):
        super().__init__(parent)
        self.ui = Ui_ExportDialog()
        self.ui.setupUi(self)
        ui = self.ui

        for name in ["E"] + list(FIELD_LABELS):
            if name not in result.fields:
                continue
            label = "E-field" if name == "E" else FIELD_LABELS[name][0]
            item = QListWidgetItem(label)
            item.setToolTip(f"Saved as {name}.<format>")
            item.setData(Qt.UserRole, name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if name in ("E", "En") else Qt.Unchecked)
            ui.fieldList.addItem(item)

        ui.tissueCombo.addItem("All tissues", "")
        for tissue in result.tissues:
            ui.tissueCombo.addItem(tissue, tissue)
        ui.folderEdit.setText(str(folder))
        ui.browseButton.clicked.connect(self.browse)
        ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("Export")

    def browse(self):
        path = QFileDialog.getExistingDirectory(
            self, "Export to", self.ui.folderEdit.text()
        )
        if path:
            self.ui.folderEdit.setText(path)

    def values(self):
        ui = self.ui
        names = []
        for row in range(ui.fieldList.count()):
            item = ui.fieldList.item(row)
            if item.checkState() == Qt.Checked:
                names.append(item.data(Qt.UserRole))
        return {
            "names": names,
            "tissue": ui.tissueCombo.currentData() or None,
            "fmt": ui.formatCombo.currentText(),
            "directory": Path(ui.folderEdit.text()),
            "mesh": ui.meshCheck.isChecked(),
        }
