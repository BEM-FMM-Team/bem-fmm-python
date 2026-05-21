import numpy as np

from bemf4_surface_field_electric_accurate import bemf4_surface_field_electric_accurate


def bemf4_electrode_current(
    c, Center, Area, normals, EC, prec, ElectrodeIndexes, condin
):
    """Computes the electrode currents"""

    #  Find total electrode currents at the electrodes
    En = bemf4_surface_field_electric_accurate(c, Center, Area, normals, EC, prec)

    electrodeCurrents = np.zeros((range(len(ElectrodeIndexes)), 1))

    for j, index in enumerate(ElectrodeIndexes):
        electrodeCurrents[j] = -np.sum(
            (En[index] * Area[index] * condin[index]), axis=0
        )

    return electrodeCurrents, En
