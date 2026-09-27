import numpy as np

from .surface_field_electric_accurate import surface_field_electric_accurate


def electrode_current(c, Center, Area, normals, EC, prec, ElectrodeIndexes, condin):
    """Computes the electrode currents"""

    #  Find total electrode currents at the electrodes
    En = surface_field_electric_accurate(c, Center, Area, normals, EC, prec)

    Area = np.ravel(Area)
    condin = np.ravel(condin)

    electrodeCurrents = np.zeros(len(ElectrodeIndexes))

    for j, index in enumerate(ElectrodeIndexes):
        electrodeCurrents[j] = -np.sum(En[index] * Area[index] * condin[index])

    return electrodeCurrents, En
