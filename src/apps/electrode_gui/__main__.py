import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from PySide6.QtWidgets import QApplication
from vedo import Mesh

from bemfmm.gui.electrode_frontend import ElectrodeFrontend
from bemfmm.lib import get_asset_path

app = typer.Typer()


@app.command()
def main(tissue_index: Optional[str] = None):
    head_models = {}

    if tissue_index:
        print("Using custom tissue_index")
        path = Path(tissue_index)
        if not path.is_file():
            raise ValueError(
                f"Invalid tissue index path is missing from {tissue_index}"
            )
    else:
        print("Using default tissue_index")
        tissue_index = get_asset_path(f"tissue_index.yaml")

    with open(tissue_index, "r") as f:
        d = f.read()
        data = yaml.safe_load(d)

    shells: dict[str, tuple[float, str, str]] = data.get("shells")
    if not shells:
        raise ValueError(f"shells is missing from {tissue_index}")

    root = Path(tissue_index).parent.resolve()

    for name, value in shells.items():
        cond, neighbour, path = value
        absolute = root / path

        print(absolute)

        mesh = Mesh(absolute)
        mesh.vertices *= 1e-3
        head_models[name] = mesh

    qapp = QApplication(sys.argv)

    frontend = ElectrodeFrontend(head_models, tissue_index)

    frontend.show()

    qapp.exec()


if __name__ == "__main__":
    app()
