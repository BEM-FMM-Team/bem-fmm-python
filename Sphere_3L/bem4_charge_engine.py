#   This script computes the induced surface charge density for an
#   inhomogeneous multi-tissue object given the primary electric field, with
#   accurate neighbor integration
#
#   Copyright SNM/WAW 2017-2020


import sys
sys.path.insert(1, '../ChargeEngine/')
# sys.path.append('../ChargeEngine/')

from bemf4_surface_field_lhs import bemf4_surface_field_lhs
from bemf4_surface_field_electric_plain import bemf4_surface_field_electric_plain
from bemf4_surface_field_potential_accurate import bemf4_surface_field_potential_accurate
from MatlabEngines.PyChargeEngine01.bemf4_surface_field_electric_accurate.py import bemf4_surface_field_electric_accurate

##  Parameters of the iterative solution
iter    = 50;     # Maximum possible number of iterations in the solution
relres  = 1e-6;   # Minimum acceptable relative residual
prec    = 1e-2;   # FMM precision
weight  = 1/2;    # Current conservation law in the weak form


Polarization = np.array([1 0 0]);
Epri, Ppri = bemf3_inc_field_electric_constant(Center, Polarization);
b        = 2 * (contrast * sum(normals * Epri, 2));                         #  Right-hand side of the BEM-FMM equation

##  GMRES iterative solution (native MATLAB GMRES is used)
# h           = waitbar(0.5, 'Please wait - Running MATLAB GMRES');
tic
#   MATVEC is the user-defined function of c equal to the left-hand side of the matrix equation LHS(c) = b
MATVEC = @(c) bemf4_surface_field_lhs(c, Center, Area, contrast, normals, weight, EC, prec);
c, its, resvec = fgmres(MATVEC, b, relres, 'restart', iter, 'max_iters', 1, 'x0', b);
# close(h);

figure
RESVEC = [];
for m = 1:size(resvec, 2)
    if m == size(resvec, 2)
        RESVEC = [RESVEC; resvec(1:its(2), m)];
    else
        RESVEC = [RESVEC; resvec(:, m)];
    end
end
semilogy(RESVEC, '-o'); grid on;
title('Relative residual of the iterative solution');
xlabel('Iteration number');
ylabel('Relative residual');


##   Find surface electric potential
Padd = bemf4_surface_field_potential_accurate(c, Center, Area, PC);
Ptot = Ppri + Padd;     #   Continuous total electric potential at interfaces

##   Find surface E-field and current density
En   = bemf4_surface_field_electric_accurate(c, Center, Area, normals, EC, prec);
J    = -En*condin;
