import numpy as np
from mesh_fix import mesh_fix
from sklearn.neighbors import NearestNeighbors


def mesh_clean_coincident_facets(
    P, t, normals, centroids, areas, Indicator, condin, condout, contrast, accuracy
):
    #   This function searches for facets that are duplicates of other facets, or otherwise have centroids that are
    #   too close together to be properly treated by BEM-FMM.  It removes one copy of each of these duplicate facets
    #   to ensure that the algorithm executes properly.

    #   Copyright WAW/SNM 2019-2024
    eps = accuracy

    # ---Find nearest neighbors for every facet---
    print(" Evaluating nearest neighbors ...")
    nbrs = NearestNeighbors(n_neighbors=2).fit(centroids)
    index, DIST = nbrs.kneighbors(centroids)
    # Now find entries where DIST is zero
    index_trimmed = index[DIST[:, 1] < eps, :]
    index_trimmed = np.sort(index_trimmed, axis=1)[
        :, ::-1
    ]  # Higher index first in each row
    index_trimmed = index_trimmed[
        np.lexsort((index_trimmed[:, 1], index_trimmed[:, 0]))
    ]  # Order rows lowest to highest
    k = np.arange(len(index_trimmed))  # Every other row is a duplicate
    index_trimmed = index_trimmed[k % 2 == 0]  # Delete duplicate rows

    # Now find the facets associated with each index
    facetList1 = t[index_trimmed[:, 0], :]
    facetList2 = t[index_trimmed[:, 1], :]

    # ---Check that coincident facets have identical vertices---
    print(" Evaluating coincident facets ...")
    coincidentFacetsCounter = 0
    coincidentCentroidsCounter = 0
    coincidentFacets = -np.ones(
        (facetList1.shape[0], 2), dtype=int
    )  # python begins indexing at 0, so 0 may not be used as a null value. Instead, we will use -1.
    coincidentCentroids = -np.ones((facetList1.shape[0], 2), dtype=int)
    for j in range(facetList1.shape[0]):
        # Can probably do this outside the for loop - assign vertices1 and
        # vertices2 exactly as they are, but replace 'j' with ':'.  If it turns
        # out that one pair of rows doesn't match, take int(rownumber)/3+1 to
        # find offending entry in facetList.
        vertices1 = P[facetList1[j], :]
        vertices2 = P[facetList2[j], :]
        # Make sure the vertices are listed in the same order
        # (Need to do this intelligently if we want to take this outside the
        # for loop)
        # vertices1 = vertices1[np.lexsort(vertices1.T[::-1])] #descending
        # vertices2 = vertices2[np.lexsort(vertices2.T[::-1])]
        vertices1 = vertices1[
            np.lexsort((vertices1[:, 2], vertices1[:, 1], vertices1[:, 0]))
        ]
        vertices2 = vertices2[
            np.lexsort((vertices2[:, 2], vertices2[:, 1], vertices2[:, 0]))
        ]
        # Check for coincident vertices
        if np.all(np.abs(vertices1 - vertices2) < eps):
            coincidentFacetsCounter += 1
            coincidentFacets[coincidentFacetsCounter - 1, :] = index_trimmed[j, :]
        else:
            coincidentCentroidsCounter += 1
            coincidentCentroids[coincidentCentroidsCounter - 1, :] = index_trimmed[j, :]

    # Clean out unused rows (modified)
    coincidentFacets = coincidentFacets[coincidentFacets[:, 0] != -1]
    coincidentCentroids = coincidentCentroids[coincidentCentroids[:, 0] != -1]

    print(f" Found {coincidentFacetsCounter} duplicate facets")
    if coincidentCentroidsCounter != 0:
        print(
            f"    Potential error: centroids coincide but the vertices do not. Correcting {len(coincidentCentroids)} facets"
        )
        # This is an error because the odds of encountering this case are
        # vanishingly small.  One way to handle it gracefully would be to pull the
        # offending centroids' vertices apart by a very small distance.
        # warning(['Found ' num2str(coincidentCentroidsCounter) ' facets with coincident centroids that do not have coincident vertices.  Resolving by perturbing vertices of both meshes']);
        # Pull offending vertices apart
        bad_idx = coincidentCentroids[coincidentCentroids != -1]  #  trim
        bad_idx = np.unique(bad_idx)
        centroids[bad_idx, :] = (
            centroids[bad_idx, :] - eps * normals[bad_idx, :]
        )  # dimensional mismatch in matlab
    else:
        print(f"    No errors found: Correcting {len(coincidentCentroids)} facets")

    # ---Update conductivity information for duplicated facets---
    print("  Resolving duplicate facets ...")
    if len(coincidentFacets) != 0:
        # coincidentFacets(:, 1) - "next" volumetric tissue next (can be different at different locations)
        # coincidentFacets(:, 2) - "previous" volumetric tissue (can be different at different locations)
        keepFacet = np.minimum(coincidentFacets[:, 0], coincidentFacets[:, 1])
        deleteFacet = np.maximum(
            coincidentFacets[:, 0], coincidentFacets[:, 1]
        )  #    Delete facets of "previous" volumetric tissue (from the list, random)
        condout[keepFacet] = condin[
            deleteFacet
        ]  #    Outer conductivity of surface becomes conductivity of volumetric tissue "previous"
        condin[keepFacet] = condin[
            keepFacet
        ]  #    Inner conductivity of surface remains conductivity of volumetric tissue "next"
        contrast[keepFacet] = (condin[keepFacet] - condout[keepFacet]) / (
            condin[keepFacet] + condout[keepFacet]
        )  # correct
        contrast[np.isnan(contrast)] = 0  #
        normals[keepFacet] = normals[
            keepFacet
        ]  #    Normal vectors must be those for "next" volumetric tissue

        # ---Now, delete duplicated facets and all associated information---
        areas = np.delete(
            areas, deleteFacet, axis=0
        )  #   Areas of "previous" volumetric tissue are deleted
        centroids = np.delete(
            centroids, deleteFacet, axis=0
        )  #  Centroids of "previous" volumetric tissue are deleted
        Indicator = np.delete(
            Indicator, deleteFacet
        )  #   Indicators of "previous" volumetric tissue are deleted
        normals = np.delete(
            normals, deleteFacet, axis=0
        )  #   Normals of "previous" volumetric tissue are deleted
        t = np.delete(
            t, deleteFacet, axis=0
        )  #   Triangles of "previous" volumetric tissue are deleted
        condin = np.delete(
            condin, deleteFacet
        )  #   All other infpormation for "previous" volumetric tissue are deleted
        condout = np.delete(condout, deleteFacet)
        contrast = np.delete(contrast, deleteFacet)

    # Remove unreferenced vertices
    P, t, _ = mesh_fix(P, t, 0)

    return P, t, normals, centroids, areas, Indicator, condin, condout, contrast
