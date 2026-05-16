from .lib import size, dot, repmat


# Computes potential and electric field for the constant field
def bemf3_inc_field_electric_constant(Points, Polarization):
    Epri = repmat(Polarization, size(Points, 0), 1)
    Ppri = -dot(Epri, Points, 1)
    return Epri, Ppri
