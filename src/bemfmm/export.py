from pathlib import Path

import numpy as np
from scipy.io import savemat

from bemfmm.mesh import mesh_areas, mesh_fix, mesh_tricenter
from bemfmm.model import HeadModel


def export_matlab(model: HeadModel, out):
    """
    Writes the combined mesh as the CombinedMesh.mat that bem01_load_model.m
    loads, so matlab and python solve the same model
    """
    # matlab model is in mm, double precision and 1-based
    P = np.asarray(model.P, dtype=np.float64) * 1e3
    t = model.t
    normals = np.asarray(model.normals, dtype=np.float64)
    center = mesh_tricenter(P, t)
    area = mesh_areas(P, t)
    contrast = model.contrast
    contrast[np.isnan(contrast)] = 0

    # same selection as script04_create_combined_mesh.m
    index = (model.interface[:, 0] == 0) & (contrast == 1)
    Ps, ts, _ = mesh_fix(P, t[index])

    surfimprint = {
        # linear indices, bem04 only uses it to delete rows
        "index": np.flatnonzero(index).reshape(-1, 1) + 1.0,
        "t": ts + 1.0,
        "normals": normals[index],
        "P": Ps,
    }

    savemat(
        Path(out),
        {
            "model": "bem-fmm-python",
            "label": np.array(model.names, dtype=object),
            "condinner": np.array(model.condinner, dtype=float).reshape(-1, 1),
            "condouter": np.array(model.condouter, dtype=float).reshape(-1, 1),
            "P": P,
            "t": t + 1.0,
            "normals": normals,
            "interface": model.interface + 1.0,
            "Area": area,
            "Center": center,
            "condin": model.condin.reshape(-1, 1),
            "condout": model.condout.reshape(-1, 1),
            "contrast": contrast.reshape(-1, 1),
            "surfimprint": surfimprint,
        },
        do_compression=True,
    )
