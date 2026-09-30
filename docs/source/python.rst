Python
======

The gui and the command line are thin layers over a few classes. Scripts can
use them directly, for parameter sweeps or batch runs.

Units are SI everywhere (m, S/m, V, A/s). Mesh files are read in mm and scaled
when a model is loaded.

Models
------

.. code-block:: python

    from bemfmm.model import HeadModel, default_index, sphere_index

    model = HeadModel.load("my_model/tissue_index.yaml")   # or default_index()
    model.names                  # tissue names, outermost first as in the index
    model.num_facets
    P, t = model.surface("gm")   # one tissue as its own mesh
    idx = model.facets("gm")     # boolean mask into the combined mesh

``read_index``, ``check_shells`` and ``write_index`` read, check and write
tissue index files.

TMS
---

.. code-block:: python

    import numpy as np
    from bemfmm.coils import default_params, make_coil
    from bemfmm.coils.rotation import vector_to_quat
    from bemfmm.solvers import tms
    from bemfmm.solvers.tms import TMSOptions

    coil = make_coil("figure_eight", default_params("figure_eight"))
    coil.place(np.array([0.042, 0.0, 0.080]), vector_to_quat([0.45, 0.0, 1.0]))
    coil.dIdt = 9.4e7

    result = tms.solve(model, [coil], TMSOptions(iter=50, relres=1e-6))

``place(center, quaternion)`` moves a coil: the quaternion is x, y, z, w and
``vector_to_quat`` gives the one that points the coil axis along a vector.
``default_coil()`` is the coil ``bemfmm tms`` uses without a setup,
``load_template(name)`` reads a strcoil template, ``COIL_TYPES`` lists the
generators.

TES
----

.. code-block:: python

    from bemfmm.electrode import Electrode
    from bemfmm.solvers import tdcs
    from bemfmm.solvers.tdcs import TDCSOptions

    electrodes = [
        Electrode("anode", [-0.016, 0.065, 0.057], radius=0.015, voltage=1.0),
        Electrode("cathode", [-0.040, 0.018, 0.064], radius=0.015, voltage=-1.0),
    ]
    result = tdcs.solve(model, electrodes, TDCSOptions(skin="skin"))

    for e in result.info["electrodes"]:
        print(e["name"], e["solved_voltage"], e["current"])

The electrode centers do not need to be on the skin, each one is moved to the
nearest facet of the ``skin`` tissue before it is imprinted.

Results
-------

Every solver returns a ``Result``:

.. code-block:: python

    result.fields.keys()         # c, E, Emag, En, Jn and Pot for TES
    result.on("Emag", "gm")      # values on one tissue
    result.info                  # settings, timings, iterations, currents
    result.resvec                # GMRES residual per iteration

    from bemfmm.results import Result

    result.save("run01")         # result.json and result.npz
    again = Result.load("run01")

    # one file per field, here only the gray matter facets, with the mesh
    result.export("run01/export", ["E", "En"], fmt="mat", tissue="gm", mesh=True)

Slices
------

.. code-block:: python

    from bemfmm.planes import Plane, axis_planes
    from bemfmm.plot.results import compute_slices
    from bemfmm.plot.slice import draw_efield_slice, load_slices, save_slices

    # the axis planes through a point, and the plane y = x
    planes = axis_planes((0.030, -0.012, 0.054)) + [Plane((1, -1, 0), (0, 0, 0))]
    slices = compute_slices(result, planes, "gm", coils=[coil])
    save_slices("run01/slices.npz", planes, slices, result.tissues)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    draw_efield_slice(fig, ax, slices[1], result.tissues, color="black")
    fig.savefig("xz.png")

A ``Plane`` is a normal, of any length, and a point on it in meters.
``compute_slices`` returns one slice per plane. The color range comes from the
field on the named tissue. For TMS pass the coils, so the primary field is
included. ``draw_efield_slice`` takes ``outside=False`` to leave the air
around the head empty, ``log=False`` for a linear scale, ``factor`` for the
log scale and ``limits=(low, high)`` in V/m.

Setups
------

.. code-block:: python

    from bemfmm.scene import Scene

    scene = Scene.load("setup.json")
    scene.coils, scene.electrodes, scene.planes, scene.mode, scene.skin

A sweep
-------

.. code-block:: python

    import numpy as np
    from bemfmm.coils import default_params, make_coil
    from bemfmm.coils.rotation import axis_angle_to_quat, quat_multiply, vector_to_quat
    from bemfmm.solvers import tms

    center = np.array([0.042, 0.0, 0.080])
    tilt = vector_to_quat([0.45, 0.0, 1.0])
    coil = make_coil("figure_eight", default_params("figure_eight"))
    for angle in range(0, 180, 30):
        twist = axis_angle_to_quat(np.array([0, 0, 1]), np.deg2rad(angle))
        coil.place(center, quat_multiply(tilt, twist))
        result = tms.solve(model, [coil])
        print(angle, np.percentile(result.on("Emag", "gm"), 99))
