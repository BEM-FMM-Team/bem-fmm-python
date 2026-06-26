from engines.gui.coil import Coil
from scipy.io import loadmat
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "coil_models"

def load_template(name):
    # creates a coil object from a file name
    cad_file = MODEL_DIR / f"{name}CAD.mat"
    str_file = MODEL_DIR / f"{name}.mat"

    template = Coil()

    cad_data = loadmat(cad_file, squeeze_me=True)
    str_data = loadmat(str_file, squeeze_me=True)

    def extract_vertices(mat):
        return np.asarray(mat["P"], dtype=float)
    
    def extract_faces(mat):
        return np.asarray(mat["t"], dtype=float)
    
    def extract_string(mat):
        return np.asarray(mat["strcoil"]["Pwire"].item(), dtype=float), np.asarray(mat["strcoil"]["Ewire"].item(), dtype=int), np.asarray(mat["strcoil"]["Swire"].item(), dtype=float).reshape(-1, 1)

    cad_P = extract_vertices(cad_data)

    template.name = name
    template.type = name
    template.t = extract_faces(cad_data)
    template.t = template.t.astype(np.int64) - 1
    template.cad_template_P = np.array(cad_P, dtype=float)
    template.str_template_P, template.Ewire, template.Swire = extract_string(str_data)

    template.cad_template_P = template.cad_template_P - np.sum(template.cad_template_P, axis = 0) / len(template.cad_template_P)
    template.str_template_P = template.str_template_P - np.sum(template.str_template_P, axis = 0) / len(template.str_template_P)

    return template