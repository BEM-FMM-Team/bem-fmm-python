import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox

from bemfmm.lib import get_asset_path, launch_detached_new_terminal

from .tms_frontend import TMSOptionsDialog

PKL_FILTER_STR = "Pickle Files (*.pkl);;All Files (*)"

SRC = Path(__file__).parent.resolve().parent.resolve().parent.resolve()
TDCS_SCRIPT = SRC / "apps/tdcs"


class TDCSOptionsDialog(TMSOptionsDialog):
    # same options as tms, with the tdcs solver defaults
    def __init__(
        self, parent=None, indexPath: str | Path = get_asset_path("tissue_index.yaml")
    ):
        super().__init__(parent, indexPath)

        self.setWindowTitle("tDCS Options")
        self.ui.iterations.setValue(50)
        self.ui.relres.setValue(1e-6)


def run_tdcs_gui(indexPath=get_asset_path("tissue_index.yaml"), electrodePath=None):
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    if electrodePath is None:
        electrodePath, _ = QFileDialog.getOpenFileName(
            None,
            "Load Electrode Configuration",
            "",
            PKL_FILTER_STR,
        )

        if not electrodePath:
            return

    path = Path(electrodePath)

    if not path.is_file():
        QMessageBox.warning(
            None,
            "Failed to run tDCS",
            f"Could not load file:\n{path}",
        )
        return

    dialog = TDCSOptionsDialog(indexPath=indexPath)

    if dialog.exec() != QDialog.Accepted:
        return

    values = dialog.get_values()

    cli_args = [
        "--electrode-path",
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

    launch_detached_new_terminal(TDCS_SCRIPT, cli_args)
