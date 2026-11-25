import numpy as np

from .mesh_fix import mesh_fix
from .mesh_normals import mesh_normals
from .mesh_reorient import mesh_reorient


def mesh_combine_interfaces(Pcell, tcell, condinner, condouter, tol_v=1e-8):
    """Weld coincident surfaces and assign conductivities across shared faces."""
    count = len(tcell)
    if not count or len(Pcell) != count:
        raise ValueError("Pcell and tcell must contain the same nonzero number of meshes")
    if len(condinner) != count or len(condouter) != count:
        raise ValueError("Each mesh must have one inside and outside conductivity")
    if tol_v <= 0:
        raise ValueError("tol_v must be positive")

    vertices, triangles, compartments = [], [], []
    vertex_offset = 0
    for compartment, (points, faces) in enumerate(zip(Pcell, tcell)):
        points = np.asarray(points, dtype=np.float64)
        faces = np.asarray(faces, dtype=np.int64)
        original_normals = mesh_normals(points, faces)
        points, faces, _ = mesh_fix(points, faces)
        faces = mesh_reorient(points, faces, original_normals)
        vertices.append(points)
        triangles.append(faces + vertex_offset)
        compartments.append(np.full(len(faces), compartment, dtype=np.int32))
        vertex_offset += len(points)

    points = np.vstack(vertices)
    faces = np.vstack(triangles)
    compartments = np.concatenate(compartments)

    quantized = np.rint(points / tol_v).astype(np.int64)
    _, representatives, old_to_new = np.unique(
        quantized, axis=0, return_index=True, return_inverse=True
    )
    points = points[representatives]
    faces = old_to_new[faces]

    nondegenerate = (
        (faces[:, 0] != faces[:, 1])
        & (faces[:, 0] != faces[:, 2])
        & (faces[:, 1] != faces[:, 2])
    )
    faces = faces[nondegenerate]
    compartments = compartments[nondegenerate]

    keys = np.sort(faces, axis=1)
    _, first_faces, groups = np.unique(
        keys, axis=0, return_index=True, return_inverse=True
    )
    faces = faces[first_faces]
    kept = compartments[first_faces]
    counts = np.bincount(groups, minlength=len(first_faces))

    order = np.argsort(groups, kind="stable")
    starts = np.cumsum(counts) - counts
    grouped_compartments = compartments[order]
    neighbor = kept.copy()

    paired = counts == 2
    neighbor[paired] = grouped_compartments[starts[paired] + 1]
    for group in np.flatnonzero(counts > 2):
        members = grouped_compartments[starts[group] : starts[group] + counts[group]]
        others = members[members != kept[group]]
        if len(others):
            values, frequencies = np.unique(others, return_counts=True)
            neighbor[group] = values[np.argmax(frequencies)]

    inner = np.asarray(condinner, dtype=np.float64)
    outer = np.asarray(condouter, dtype=np.float64)
    condin = inner[kept]
    condout = outer[kept].copy()
    matched = neighbor != kept
    condout[matched] = inner[neighbor[matched]]

    interface = np.column_stack((kept, neighbor))
    normals = mesh_normals(points, faces)
    return points, faces, normals, condin, condout, interface
