import sys
from pathlib import Path

import numpy as np
from vedo import Mesh

BASE_DIR = Path(__file__).resolve().parent
root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))
#print(f"Setup environment {root_dir}")

test_dir = Path(__file__).resolve().parent.resolve().parent
ASSETS = (test_dir / "assets").resolve()

from engines.gui.gui_frontend import Frontend


skin_path = ASSETS / "skin.stl"
head = Mesh(str(skin_path))
head.vertices *= 1e-3
frontend = Frontend(head,["ring", "figure_eight", "figure_eightX", "MagVenture_Cool_B35", "MagVenture_C_B60", "MagVenture_Cool40_Rat", "MagVenture_D_B80", "MagVenture_MRiB91", "MagVenture_TMSMEG"])
frontend.activate()