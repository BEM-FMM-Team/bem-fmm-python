from .lib import msum, mul, zeros

from bemf4_surface_field_electric_accurate import bemf4_surface_field_electric_accurate


#  Computes the electrode currents
def bemf4_electrode_current(
    c, Center, Area, normals, EC, prec, ElectrodeIndexes, condin
):
    #  Find total electrode currents at the electrodes
    En = bemf4_surface_field_electric_accurate(c, Center, Area, normals, EC, prec)

    electrodeCurrents = zeros(range(len(ElectrodeIndexes)), 1)

    for j, index in enumerate(ElectrodeIndexes):
        electrodeCurrents[j] = -msum(mul(En[index], Area[index], condin[index]))

    return electrodeCurrents, En
