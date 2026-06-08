import numpy as np

from engines.charge.bemf3_inc_field_electric_gauss_selective_dipoles import \
    bemf3_inc_field_electric_gauss_selective_dipoles
from engines.lib import timeit
from engines.plot.patch import patch


@timeit
def setup_dipoles(
    P,
    t,
    normals,
    Center,
    Area,
    contrast,
    condinner,
    condin,
    condouter,
    condout,
    tissuename,
):
    """
    Setup Dipoles
    Setup the dipoles and compute the primary field for bem-fmm

    DD - 5/2026
    """
    ## Fixed dipole positions
    # Will start with a single dipole at the origin (pointing up).
    dipPlus = 1e-3 * np.array([-20, 15, 40])
    dipMinus = 1e-3 * np.array([-20, 15.1, 40.1])

    # Total Current
    Itot = 1e-3
    # 1 [mA]

    ## Dipole values

    # Values necessary for calculating the primary field
    dipVec = dipPlus - dipMinus
    strdipolePplus = dipPlus
    strdipolePminus = dipMinus
    Ctr = (dipMinus + dipPlus) / 2
    NoDipoles = dipPlus.shape[0]
    I0 = Itot / NoDipoles
    # ensure that the total strength is 1e-5 A

    strdipoleCurrent = np.hstack(
        [I0 * np.ones((1, NoDipoles)), -I0 * np.ones((1, NoDipoles))]
    )
    # TODO check for vstack
    condLAST = condinner[-1]
    # innermost tissue index
    strdipolesig = condLAST * np.ones((1, 2 * NoDipoles))
    strdipolemcenter = Ctr
    strdipolemstrength = Itot
    strdipolemvector = strdipolePplus - strdipolePminus

    ## Primary Field
    # Compute the primary field and rhs vector

    """
    Epri, Ppri = bemf3_inc_field_electric(
        strdipolePplus,
        strdipolePminus,
        strdipolesig,
        strdipoleCurrent,
        P,
        t,
        Center,
        Area,
        normals,
        1e-2,
        0,
        0,
    )
    ## b            = 2*(contrast.*sum(normals.*Epri, 2)); C = b.*Area; #  Right-hand side of the BEM-FMM equation
    """

    R = 1
    gaussRadius = 2 * R
    dipoleClusterCenter = np.mean(Ctr, axis=0)

    Epri, Ppri = bemf3_inc_field_electric_gauss_selective_dipoles(
        strdipolePplus=strdipolePplus,
        strdipolePminus=strdipolePminus,
        strdipolesig=strdipolesig,
        strdipoleCurrent=strdipoleCurrent,
        P=P,
        t=t,
        Center=Center,
        dipoleClusterCenter=dipoleClusterCenter,
        gaussRadius=gaussRadius,
    )

    ## Plot primary field
    Eprin = np.sum(Epri * normals, 1)
    plot_t_idx = np.ones(t.shape[0], dtype=bool)
    plot_t = t[plot_t_idx]
    plot_field = Eprin[plot_t_idx]

    viewax = np.array([-120, 20])  # TODO embed

    patch(
        vertices=P,
        faces=plot_t,
        cdata=plot_field,  # replaces p.FaceVertexCData = plot_field
        edge_color="none",
        title=rf"Primary Field Eⁱ on Surface: {tissuename[0]}",
        cmap_label="A/m²",
    ).show()

    # Figure plot
    # fig = figure("Name","Plot Test");
    # p = patch('Vertices',P,'Faces',t(plot_t_idx,:));
    # p.FaceVertexCData = plot_field;
    # p.EdgeColor = "none";
    # p.FaceColor = "flat";
    #
    # # Colormap and Colorbar
    # cmap = "jet";
    # colormap(cmap);
    # cb = colorbar;
    # cb.Label.String = ;
    #
    # # Axis background color
    # set(gca,"Color","k")
    #
    # # Camview
    # view(viewax(1),viewax(2))
    # camlight
    # axis equal
    #
    # # Set figure font
    # set(findall(gcf, '-property', 'FontName'), 'FontName', 'Times New Roman');
    #
    # # Set text interpreter to latex
    # set(findall(fig, "Type", "text"), "Interpreter", 'latex')
    # set(findall(cb.Label, "Type", "text"), "Interpreter", 'latex')
    #
    # # Draw axis into figure
    # drawnow;
