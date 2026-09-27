Files
=====

Tissue index
------------

A ``.yaml`` file that lists the tissues of a model, one closed surface each:

.. code-block:: yaml

    shells:
      skin : [0.4650, "FreeSpace", "skin.stl"]
      bone : [0.010,  "skin",      "bone.stl"]
      gm   : [0.2750, "bone",      "gm.stl"]

Each row is ``name : [conductivity inside in S/m, tissue outside, mesh file]``.
The outside tissue must be another row or ``FreeSpace`` (air). Mesh paths are
relative to the index file and the meshes are in mm. Normals must point out of
the tissue.

Setup
-----

A ``.json`` file written by the gui (File > Save setup) and read by
``bemfmm tms --setup`` and ``bemfmm tdcs --setup``:

.. code-block:: json

    {
      "version": 1,
      "tissue_index": "C:/models/subject01/tissue_index.yaml",
      "mode": "tdcs",
      "skin": "skin",
      "planes": [0.0, 0.0, 0.01],
      "coils": [
        {"name": "figure_eight 1", "type": "figure_eight", "params": {"...": "..."},
         "com": [0.046, -0.012, 0.083], "rot": [0.13, 0.13, 0.39, 0.90],
         "distance": 0.01, "dIdt": 1e8}
      ],
      "electrodes": [
        {"name": "E0", "center": [0.0, 0.0, 0.042], "normal": [0.0, 0.0, 1.0],
         "radius": 0.008, "voltage": 1.0}
      ]
    }

Lengths are in meters, ``rot`` is a quaternion (x, y, z, w) and ``dIdt`` is in
A/s. ``mode`` is the kind of study the setup was made for and ``skin`` the
surface the coils and electrodes sit on, both may be missing in older setups.
Coils are stored by type and parameters and rebuilt when the setup is read, a
``template`` coil stores the path of its ``.mat`` file.

Run folder
----------

Each run from the gui gets its own folder:

======================= ======================================================
``setup.json``          exactly what was solved
``tissue_index.yaml``   only when the tissues were edited but not saved
``result.json``         run information
``result.npz``          mesh and per facet fields
``slices.npz``          E-field slices, when they were computed
``*.mat`` and others    fields exported with Also export or Export fields
======================= ======================================================

``result.json`` holds the kind of run, the tissue names, the solver options,
the number of iterations and final residual, timings per stage, the date, the
package version and git commit, and the fingerprint of the model it was solved
on. tDCS results also list every electrode with its facets, set and solved
voltage and current, the total current and the power. TMS results list the
coils and how well the normal current is continuous across the surfaces
(``current_conservation``, the norm of the jump in normal current times area).

``result.npz`` holds ``P`` and ``t`` (the combined mesh, 0 based), ``normals``,
``interface`` (inside and outside tissue of every facet), ``resvec`` and one
``field_<name>`` array per field:

=========== =========================================================
``c``       surface charge density divided by eps0 (V/m)
``E``       continuous E-field at the facet centers, N x 3 (V/m)
``Emag``    magnitude of ``E`` (V/m)
``En``      normal component of the continuous E-field (V/m)
``Jn``      outward normal current density just inside the surface (A/m^2)
``Pot``     surface potential, tDCS only (V)
=========== =========================================================

tDCS results also store ``electrodes``, the electrode number of every facet
(0 for none).

Slices
------

``slices.npz`` holds, for each plane ``XY``, ``XZ`` and ``YZ``, the grid
axes ``<plane>_u`` and ``<plane>_v``, the field on the grid (``<plane>_E_mag``
and the log scaled ``<plane>_E_grid``), the color limits and the tissue
outlines (``<plane>_points_2d``, ``<plane>_edges``, ``<plane>_ci``). ``planes``
has the plane positions in meters, ``tissues`` the tissue names and ``created``
the date of the result the slices belong to. Load it with
``bemfmm.plot.slice.load_slices``.

Exported fields
---------------

One file per field, named after it (``En.mat``, ``E_gm.mat`` when only one
tissue was exported). Scalar fields are one column, ``E`` three. With the mesh
included, ``P`` is in meters and ``t`` counts from 1 in ``.mat`` files, from 0
otherwise.

MATLAB model
------------

``bemfmm export-matlab`` writes ``CombinedMesh.mat`` with the combined mesh in
mm and 1 based indices, for the MATLAB scripts.
