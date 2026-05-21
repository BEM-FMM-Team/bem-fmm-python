import numpy as np

def bemf3_inc_field_electric_gauss_selective_dipoles(SourceDipole = None,P = None,t = None,Center = None,dipoleClusterCenter = None,gaussRadius = None
                                                     ):
    strdipolePplus = SourceDipole.src_p
    strdipolePminus = SourceDipole.src_m
    strdipolesig = SourceDipole.src_sig
    strdipoleCurrent = SourceDipole.src_cur
    ## Compute model subdivision parameters
#   number of integration points in the Gaussian quadrature
#   for the outer potential integrals
#   Numbers 1, 4, 7, 13, 25 are permitted
#   Gaussian weights for analytical integration (for the outer integral)
    gauss = 7
    if gauss == 0:
        coeffS,weightsS,IndexS = mesh_tri(subdivParam)
    elif gauss == 1:
        coeffS,weightsS,IndexS = mesh_tri(1,1)
    elif gauss == 4:
        coeffS,weightsS,IndexS = mesh_tri(4,3)
    elif gauss == 7:
        coeffS,weightsS,IndexS = mesh_tri(7,5)
    elif gauss == 13:
        coeffS,weightsS,IndexS = mesh_tri(13,7)
    elif gauss == 25:
        coeffS,weightsS,IndexS = mesh_tri(25,10)
    else:
        raise Exception('Invalid Gaussian subdivision parameter')

    ## Find all triangles that require Gaussian subdivision based on distance from center of dipole cluster
    # Find indices of triangles that need to be subdivided

    # This commented-out method may be useful for multiple dipole clusters.
    # (as written, it only extracts the points close to the first cluster)
    #trianglesToSubdiv_temp = rangesearch(Center, dipoleClusterCenter, gaussRadius);
    # Convert to logical array
    #trianglesToSubdiv = logical(zeros(size(t, 1), 1));
    #trianglesToSubdiv(trianglesToSubdiv_temp{1}) = true;

    # This method is much faster for a single dipole cluster
    tempDist = vecnorm(Center - dipoleClusterCenter,2,2)
    trianglesToSubdiv = tempDist <= gaussRadius

    ## Preallocate output variables
    Epri = np.zeros((t.shape[0],3))
    Ppri = np.zeros((t.shape[0],1))

    ## Calculate incident fields on triangles that do not require subdivision
    if np.any(not trianglesToSubdiv ):
        Epri[not trianglesToSubdiv ,:],Ppri[not trianglesToSubdiv ,:] = bemf3_inc_field_electric_plain(strdipolePplus,strdipolePminus,strdipolesig,strdipoleCurrent,Center[ not trianglesToSubdiv ,: ])
    else:
        print('skipping primary at triangles which do not need subdiv.' % ())

    ## Subdivide the triangles that do require subdivision
    Center_subdiv = np.zeros((IndexS * sum(trianglesToSubdiv),3))
    P1 = P(t(trianglesToSubdiv,1),:)
    P2 = P(t(trianglesToSubdiv,2),:)
    P3 = P(t(trianglesToSubdiv,3),:)
    for j in np.arange(1,IndexS+1).reshape(-1):
        currentIndices = (np.array([np.arange(1,sum(trianglesToSubdiv)+1)]) - 1) * IndexS + j
        Center_subdiv[currentIndices,:] = coeffS(1,j) * P1 + coeffS(2,j) * P2 + coeffS(3,j) * P3

    ## Calculate incident electric fields on subdivided triangles
    E_subdiv,P_subdiv = bemf3_inc_field_electric_plain_dipoles(strdipolePplus,strdipolePminus,strdipolesig,strdipoleCurrent,Center_subdiv)
    ## Recover average electric field at whole triangles from subdivided triangles
    #Every column contains the subdivided quantities for one full triangle
    P_subdiv_temp = np.reshape(P_subdiv,IndexS,[])
    Ex_temp = np.reshape(E_subdiv[:,1],IndexS,[])
    Ey_temp = np.reshape(E_subdiv[:,2],IndexS,[])
    Ez_temp = np.reshape(E_subdiv[:,3],IndexS,[])
    ## Write to output variables
    Ppri[trianglesToSubdiv] = (weightsS * P_subdiv_temp).T
    Epri[trianglesToSubdiv,1] = (weightsS * Ex_temp).T
    Epri[trianglesToSubdiv,2] = (weightsS * Ey_temp).T
    Epri[trianglesToSubdiv,3] = (weightsS * Ez_temp).T
    return Epri,Ppri
