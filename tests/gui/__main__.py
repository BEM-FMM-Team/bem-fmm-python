import sys
from pathlib import Path

from vedo import Mesh

BASE_DIR = Path(__file__).resolve().parent
root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))
# print(f"Setup environment {root_dir}")

test_dir = Path(__file__).resolve().parent.resolve().parent
ASSETS = (test_dir / "assets").resolve()

from PySide6.QtWidgets import QApplication

from engines.gui.gui_frontend_new import Frontend


def main():
    head_models = {}

    for name in [
        "bone",
        "cerebellum",
        "csf",
        "gm",
        "skin",
        "ventricles",
        "wm",
    ]:
        path = ASSETS / f"{name}.stl"

        mesh = Mesh(str(path))
        mesh.vertices *= 1e-3

        head_models[name] = mesh

    app = QApplication(sys.argv)

    frontend = Frontend(
        head_models,
        [
            "ring",
            "figure_eight",
            "figure_eightX",
            "MagVenture_Cool_B35",
            "MagVenture_C_B60",
            "MagVenture_Cool40_Rat",
            "MagVenture_D_B80",
            "MagVenture_MRiB91",
            "MagVenture_TMSMEG",
        ],
    )

    frontend.show()

    app.exec()


if __name__ == "__main__":
    main()
