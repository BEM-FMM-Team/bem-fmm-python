from .figure_eight import figure_eight
from .figure_eightX import figure_eightX
from .MagVenture_C_B60 import MagVenture_C_B60
from .MagVenture_Cool40_Rat import MagVenture_Cool40_Rat
from .MagVenture_Cool_B35 import MagVenture_Cool_B35
from .MagVenture_D_B80 import MagVenture_D_B80
from .MagVenture_MRiB91 import MagVenture_MRiB91
from .MagVenture_TMSMEG import MagVenture_TMSMEG
from .ring import ring_gen

GENERATORS = {
    "ring": ring_gen,
    "figure_eight": figure_eight,
    "figure_eightX": figure_eightX,
    "MagVenture_Cool_B35": MagVenture_Cool_B35,
    "MagVenture_C_B60": MagVenture_C_B60,
    "MagVenture_Cool40_Rat": MagVenture_Cool40_Rat,
    "MagVenture_D_B80": MagVenture_D_B80,
    "MagVenture_MRiB91": MagVenture_MRiB91,
    "MagVenture_TMSMEG": MagVenture_TMSMEG,
}

# offered in the gui, MagVenture_C_B60 is left out until its mesh is fixed
COIL_TYPES = [
    "ring",
    "figure_eight",
    "figure_eightX",
    "MagVenture_Cool_B35",
    "MagVenture_Cool40_Rat",
    "MagVenture_D_B80",
    "MagVenture_MRiB91",
    "MagVenture_TMSMEG",
]

# generator parameters and their defaults, lengths in m
COIL_PARAMS = {
    "ring": {
        "radius": {"type": float, "default": 0.02},
        "diameter": {"type": float, "default": 0.002},
        "M": {"type": int, "default": 16},
        "flag": {"type": int, "default": 1},
        "sk": {"type": int, "default": 1},
    },
    "figure_eight": {
        "a0": {"type": float, "default": 0.01},
        "b0": {"type": float, "default": 0.001},
        "diameter": {"type": float, "default": 0.006},
        "M": {"type": int, "default": 16},
        "flag": {"type": int, "default": 2},
        "sk": {"type": int, "default": 1},
    },
    "figure_eightX": {
        "a0": {"type": float, "default": 0.01},
        "b0": {"type": float, "default": 0.001},
        "z_scale": {"type": float, "default": 0.004},
        "z_shift": {"type": float, "default": 6},
        "height": {"type": float, "default": 4e-3},
        "thickness": {"type": float, "default": 2.5e-3},
        "M": {"type": int, "default": 16},
        "flag": {"type": int, "default": 2},
        "sk": {"type": int, "default": 1},
    },
    "MagVenture_Cool_B35": {
        "turns": {"type": int, "default": 32},
        "a0": {"type": float, "default": 0.0115},
        "a": {"type": float, "default": 15.0e-3},
        "b": {"type": float, "default": 0.2e-3},
        "M": {"type": int, "default": 20},
        "flag": {"type": int, "default": 2},
        "sk": {"type": int, "default": 0},
    },
    "MagVenture_C_B60": {
        "a0": {"type": float, "default": 0.017},
        "b0": {"type": float, "default": 0.0006},
        "height": {"type": float, "default": 3.6e-3},
        "thickness": {"type": float, "default": 2.61e-3},
        "M": {"type": int, "default": 20},
        "flag": {"type": int, "default": 2},
        "sk": {"type": int, "default": 1},
    },
    "MagVenture_Cool40_Rat": {
        "a": {"type": float, "default": 3e-3},
        "b": {"type": float, "default": 0.5e-3},
        "M": {"type": int, "default": 20},
        "flag": {"type": int, "default": 2},
        "sk": {"type": int, "default": 1},
    },
    "MagVenture_D_B80": {
        "a0": {"type": float, "default": 0.024},
        "b0": {"type": float, "default": 0.00061},
        "a": {"type": float, "default": 6e-3},
        "b": {"type": float, "default": 2e-3},
        "M": {"type": int, "default": 20},
        "flag": {"type": int, "default": 2},
        "sk": {"type": int, "default": 1},
    },
    "MagVenture_MRiB91": {
        "height": {"type": float, "default": 3.5e-3},
        "thickness": {"type": float, "default": 2.2e-3},
        "M": {"type": int, "default": 32},
        "N": {"type": int, "default": 128},
        "flag": {"type": int, "default": 2},
        "sk": {"type": int, "default": 1},
    },
    "MagVenture_TMSMEG": {
        "a": {"type": float, "default": 0.0015},
        "M": {"type": int, "default": 16},
        "N": {"type": int, "default": 64},
        "flag": {"type": int, "default": 1},
        "sk": {"type": int, "default": 1},
    },
}


def default_params(coil_type):
    return {name: info["default"] for name, info in COIL_PARAMS[coil_type].items()}
