import numpy as np
from engines.gui.coil_generators.ring import ring_gen
from engines.gui.coil_generators.figure_eight import figure_eight
from engines.gui.coil_generators.figure_eightX import figure_eightX
from engines.gui.coil import Coil
from engines.gui.coil_load_gui import coil_load_gui
from engines.gui.coil_generators.MagVenture_Cool_B35 import MagVenture_Cool_B35
from engines.gui.coil_generators.MagVenture_C_B60 import MagVenture_C_B60
from engines.gui.coil_generators.MagVenture_Cool40_Rat import MagVenture_Cool40_Rat
from engines.gui.coil_generators.MagVenture_D_B80 import MagVenture_D_B80
from engines.gui.coil_generators.MagVenture_MRiB91 import MagVenture_MRiB91
from engines.gui.coil_generators.MagVenture_TMSMEG import MagVenture_TMSMEG

def load_coil_from_func(type, window_cord):
    params = coil_load_gui(type, window_cord)
    if type == "ring":
        mesh_data = ring_gen(**params)
    elif type == "figure_eight":
        mesh_data = figure_eight(**params)
    elif type == "figure_eightX":
        mesh_data = figure_eightX(**params)
    elif type == "MagVenture_Cool_B35":
        mesh_data = MagVenture_Cool_B35(**params)
    elif type == "MagVenture_C_B60":
        mesh_data = MagVenture_C_B60(**params)
    elif type == "MagVenture_Cool40_Rat":
        mesh_data = MagVenture_Cool40_Rat(**params)
    elif type == "MagVenture_D_B80":
        mesh_data = MagVenture_D_B80(**params)
    elif type == "MagVenture_MRiB91":
        mesh_data = MagVenture_MRiB91(**params)
    elif type == "MagVenture_TMSMEG":
        mesh_data = MagVenture_TMSMEG(**params)
    new_coil = Coil()
    new_coil.type = type
    new_coil.name = type

    new_coil.Ewire = mesh_data["Ewire"]
    new_coil.Swire = mesh_data["Swire"]
    new_coil.t = mesh_data["t"]
    temp_cad = mesh_data["P"]
    cad_com = np.mean(temp_cad, axis=0)
    temp_cad = temp_cad - cad_com
    temp_wire = mesh_data["Pwire"]
    wire_com = np.mean(temp_wire, axis=0)
    temp_wire = temp_wire - wire_com
    new_coil.cad_template_P = temp_cad
    new_coil.str_template_P = temp_wire

    return new_coil
