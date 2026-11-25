Files
=====

Project
-------

A project is a folder with a head model and the work done on it:

::

    my_head/
      project.yaml        name, tissue index and skin tissue
      tissue_index.yaml
      skin.stl, ...
      setups/             setup files
      runs/               one folder per run

``project.yaml``:

.. code-block:: yaml

    version: 1
    name: Subject 01
    index: tissue_index.yaml
    skin: skin
    flip_xy: true
    deduplicate_interfaces: true
    smooth_nonmanifold: true
    tissue_colors:
      skin: [1.0, 1.0, 1.0]

``index`` is relative to the project folder, ``skin`` is the tissue coils and
electrodes sit on. All keys but ``version`` may be left out, and so may the
whole file: a folder with a ``tissue_index.yaml`` is a project named after the
folder. The default head and the sphere that ship with the package are
projects too, read only, so their runs go to the output folder. The bundled
Sim4Life 40-tissue model is another read-only project preset (codename
``makaroff-40``).

``flip_xy`` applies the X/Y coordinate flip used by the Sim4Life mesh source.
``deduplicate_interfaces`` welds vertices across tissue meshes and merges
coincident triangles, assigning each shared face the conductivity of its
neighboring tissue. ``smooth_nonmanifold`` applies the prototype's pinned
Taubin smoothing to the combined mesh after interface merging. These three
processing options are off by default. ``tissue_colors`` maps
tissue names to RGB triplets in the range 0–1 or ``#RRGGBB`` values; it is
used for model surfaces and tissue outlines in slice plots.

Tissue index
------------

A ``.yaml`` file that lists the tissues of a model, one closed surface each:

.. code-block:: yaml

    shells:
      skin : [0.4650, "FreeSpace", "skin.stl"]
      bone : [0.010,  "skin",      "bone.stl"]
      gm   : [0.2750, "bone",      "gm.stl"]

Each row is ``name : [conductivity inside in S/m, tissue outside, mesh file]``.
For ordinary nested models, the outside tissue must be another row or
``FreeSpace`` (air). Mesh paths are relative to the index file and the meshes
are in mm. Normals must point out of the tissue. With
``deduplicate_interfaces`` enabled, coincident faces are treated as shared
interfaces and the outside value applies only to faces without a matching
neighboring surface.

Sim4Life 40-tissue preset
-------------------------

The bundled **Sim4Life 40-tissue head** is selectable alongside the default
head and sphere. Its preset codename is ``makaroff-40``. It includes the 40
STL surfaces from the Sim4Life model, the project-specific X/Y flip, interface
deduplication and Taubin smoothing, the supplied tDCS conductivities in S/m,
and the supplied RGB colors. Its conductivity values are stored in its own
``tissue_index.yaml``; the global **Defaults** list remains unchanged for
other projects.

Default conductivities
----------------------

The gui gives new tissues, and **Defaults** gives all of them, a conductivity
from this list (``assets/conductivities.yaml``), the standard values of
SimNIBS. A tissue is found by its name or a part of it, so ``scalp``,
``sub01_scalp.stl`` and ``lh.pial`` are found too.
For a project with ``deduplicate_interfaces: true``, **Defaults** restores
values from that project's tissue index instead. Newly added tissues still use
the global list.

================ ======= ======================================== ==================
tissue           S/m     also found as                            source
================ ======= ======================================== ==================
``skin``         0.465   scalp                                    Wagner et al. 2004
``bone``         0.010   skull                                    Wagner et al. 2004
``compact_bone`` 0.008   compact                                  Opitz et al. 2015
``spongy_bone``  0.025   spongy, cancellous                       Opitz et al. 2015
``csf``          1.654                                            Wagner et al. 2004
``ventricles``   1.654   ventricle                                as csf
``gm``           0.275   gray_matter, grey_matter, cortex, pial   Wagner et al. 2004
``wm``           0.126   white_matter, white                      Wagner et al. 2004
``cerebellum``   0.126                                            as wm
``eyes``         0.500   eye, eyeballs, eyeball                   Opitz et al. 2015
``blood``        0.600                                            Gabriel et al. 2009
``muscle``       0.160   muscles                                  Gabriel et al. 2009
================ ======= ======================================== ==================

Setup
-----

A ``.json`` file written by the gui (File > Save setup) and read by
``bemfmm tms --setup`` and ``bemfmm tes --setup``:

.. code-block:: json

    {
      "version": 2,
      "tissue_index": "C:/models/subject01/tissue_index.yaml",
      "mode": "tdcs",
      "skin": "skin",
      "planes": [
        {"normal": [0.0, 0.0, 1.0], "point": [0.0, 0.0, 0.01]},
        {"normal": [1.0, -1.0, 0.0], "point": [0.0, 0.0, 0.0]}
      ],
      "coils": [
        {"name": "figure_eight 1", "type": "figure_eight", "params": {"...": "..."},
         "com": [0.046, -0.012, 0.083], "rot": [0.13, 0.13, 0.39, 0.90],
         "distance": 0.01, "dIdt": 9.4e7}
      ],
      "electrodes": [
        {"name": "E0", "center": [0.0, 0.0, 0.042], "normal": [0.0, 0.0, 1.0],
         "radius": 0.008, "voltage": 1.0}
      ]
    }

Lengths are in meters, ``rot`` is a quaternion (x, y, z, w) and ``dIdt`` is in
A/s. ``tissue_index`` is relative to the setup when the setup is inside the
index's project folder (``../tissue_index.yaml`` for ``setups/``), so a
project can be moved or copied with its setups, and absolute otherwise. An
absolute path into ``bemfmm/assets`` that is not found, from a setup made on
another computer, opens the bundled model installed here. ``mode`` is the kind of study the setup was made for, ``tms`` or ``tdcs``
(TES, the key keeps its old name), and ``skin`` the
surface the coils and electrodes sit on, both may be missing in older setups.
``planes`` are the slice planes, each a normal and a point on it. Setups before
version 2 stored the x, y, z of the three axis planes, they still open.
Coils are stored by type and parameters and rebuilt when the setup is read, a
``template`` coil stores the path of its ``.mat`` file.

Run folder
----------

Each run from the gui gets its own folder:

======================= ======================================================
``setup.json``          exactly what was solved
``tissue_index.yaml``   only when the tissues were edited but not saved
``result.json``         run information
``result.npz``          mesh and per facet quantities
``slices.npz``          E-field slices, when they were computed
``*.mat`` and others    quantities exported with Also export or Export results
======================= ======================================================

``result.json`` holds the kind of run, the tissue names, the solver options,
the number of iterations and final residual, timings per stage, the date, the
package version and git commit, and the fingerprint of the model it was solved
on. TES results also list every electrode with its facets, set and solved
voltage and current, the total current and the power. TMS results list the
coils and how far the solved charge is from adding up to zero
(``conservation_law_error``, the total charge over the total of its absolute
value, taken before the charge is smoothed).

``result.npz`` holds ``P`` and ``t`` (the combined mesh, 0 based), ``normals``,
``interface`` (inside and outside tissue of every facet), ``resvec`` and one
``field_<name>`` array per quantity:

=========== =========================================================
``c``       surface charge density divided by eps0 (V/m)
``E``       E-field just inside the surface, averaged over the facet, N x 3 (V/m)
``Emag``    magnitude of ``E`` (V/m)
``En``      normal component of the continuous E-field (V/m)
``Jn``      outward normal current density just inside the surface (A/m^2)
``Pot``     surface potential, TES only (V)
=========== =========================================================

TES results also store ``electrodes``, the electrode number of every facet
(0 for none).

Slices
------

``slices.npz`` holds ``planes``, one row per plane with its normal and a point
on it in meters (N x 6), and for plane number ``i`` the grid axes ``s<i>_u``
and ``s<i>_v``, the E-field magnitude on the grid in V/m (``s<i>_E_mag``),
which grid points are inside the head (``s<i>_mask``), the color range
``s<i>_range`` (lowest and highest value in V/m) and the tissue outlines
(``s<i>_points_2d``, ``s<i>_edges``, ``s<i>_ci``). The grid and outlines are in
the plane's own coordinates. The log scale is applied when the slices are
drawn. ``tissues`` has the tissue names and ``created`` the date of the result
the slices belong to. Load it with ``bemfmm.plot.slice.load_slices``, which
also reads older files: keyed ``XY``, ``XZ`` and ``YZ``, and with log scaled
limits (``_limits``) instead of ``_range``. Their mask marks every point as
inside, so the field outside the head is always drawn for them.

Exported quantities
-------------------

One file per quantity, named after it (``En.mat``, ``E_gm.mat`` when only one
tissue was exported). Scalars are one column, ``E`` three. With the mesh
included, ``P`` is in meters and ``t`` counts from 1 in ``.mat`` files, from 0
otherwise.

MATLAB model
------------

``bemfmm export-matlab`` writes ``CombinedMesh.mat`` with the combined mesh in
mm and 1 based indices, for the MATLAB scripts.
