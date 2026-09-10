import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox

from bemfmm.lib import get_asset_path, launch_detached_new_terminal

from .ui_tms_dialog import Ui_OptionsDialog

PKL_FILTER_STR = "Pickle Files (*.pkl);;All Files (*)"
YAML_FILTER_STR = "Yaml Files (*.yaml *.yml);;All Files (*)"

SRC = Path(__file__).parent.resolve().parent.resolve().parent.resolve()
TMS_SCRIPT = SRC / "apps/tms"


class TMSOptionsDialog(QDialog):
    def __init__(
        self, parent=None, indexPath: str | Path = get_asset_path("tissue_index.yaml")
    ):
        super().__init__(parent)

        self.ui = Ui_OptionsDialog()
        self.ui.setupUi(self)

        self.ui.tissueIndexPath.setText(str(indexPath))
        self.ui.outputDirPath.setText(str(Path.cwd() / "__output__"))

        self.ui.browseTissueBtn.clicked.connect(self.browse_tissue_index)
        self.ui.browseOutputBtn.clicked.connect(self.browse_output_dir)

    def browse_tissue_index(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Tissue Index YAML",
            "",
            YAML_FILTER_STR,
        )

        if file_path:
            self.ui.tissueIndexPath.setText(file_path)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
        )

        if dir_path:
            self.ui.outputDirPath.setText(dir_path)

    def get_values(self):
        if self.ui.radioMat.isChecked():
            save_format = "mat"
        elif self.ui.radioCsv.isChecked():
            save_format = "csv"
        elif self.ui.radioNpz.isChecked():
            save_format = "npz"
        elif self.ui.radioPkl.isChecked():
            save_format = "pkl"
        else:
            save_format = "none"

        save = []

        if self.ui.saveE.isChecked():
            save.append("E")

        if self.ui.saveC.isChecked():
            save.append("c")

        if self.ui.saveEn.isChecked():
            save.append("En")

        return {
            "tissue_index": self.ui.tissueIndexPath.text(),
            "num_neighbors": self.ui.numNeighbors.value(),
            "output_dir": self.ui.outputDirPath.text(),
            "save_format": save_format,
            "iter": self.ui.iterations.value(),
            "relres": self.ui.relres.value(),
            "weight": self.ui.weight.value(),
            "save": save,
        }


def run_tms_gui(indexPath=get_asset_path("tissue_index.yaml")):
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    path, _ = QFileDialog.getOpenFileName(
        None,
        "Load Coil Configuration",
        "",
        PKL_FILTER_STR,
    )

    if not path:
        return

    path = Path(path)

    if not path.is_file():
        QMessageBox.warning(
            None,
            "Failed to run TMS",
            f"Could not load file:\n{path}",
        )
        return

    dialog = TMSOptionsDialog(indexPath=indexPath)

    if dialog.exec() != QDialog.Accepted:
        return

    values = dialog.get_values()

    cli_args = [
        "--coil-path",
        str(path),
        "--tissue-index",
        values["tissue_index"],
        "--num-neighbors",
        str(values["num_neighbors"]),
        "--output-dir",
        values["output_dir"],
        "--save-format",
        values["save_format"],
        "--iter",
        str(values["iter"]),
        "--relres",
        str(values["relres"]),
        "--weight",
        str(values["weight"]),
    ]

    for item in values["save"]:
        cli_args.extend(["--save", item])

    launch_detached_new_terminal(TMS_SCRIPT, cli_args)
