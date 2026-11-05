Development
===========

Setup
-----

::

    nix develop                              or, without nix:
    python -m uv pip install -e ".[dev]"
    pytest                                   about 40 s, sphere model only
    python scripts/benchmark.py              timings and reference numbers
    python scripts/benchmark.py --head       adds the full head model

The tests turn the cache off (``BEMFMM_NO_CACHE=1``) so they always solve. The
TMS and TES reference numbers in ``tests/test_solvers.py`` come from the code
before the refactor, which the current solvers reproduce to machine precision.
If a change moves them, it changed the numerics.

``benchmark.py --save before.json`` and ``--compare before.json`` check a
change against the numbers from before it.

Layout
------

::

    src/bemfmm/
      model.py        tissue index and the combined mesh (HeadModel)
      project.py      project folders (Project)
      conductivity.py the default conductivities
      coils/          Coil, generators, templates, rotations
      electrode.py    TES electrodes
      scene.py        setup files
      solvers/        tms, tdcs and uniform, with common helpers
      results.py      Result, its files and exports
      charge/         fields, potentials and near field integrals
      mesh/           mesh tools (normals, imprinting, plane cuts)
      fgmres.py       flexible GMRES
      plot/           plot windows and the slice computation
      gui/            the graphical interface
      cli.py          the bemfmm command
      export.py       CombinedMesh.mat for MATLAB
      assets/         default head model and the three layer sphere
    scripts/          sphere model generator, benchmark
    tests/

The layers only depend downwards: ``gui`` and ``cli`` use ``solvers``,
``results`` and ``plot``, the solvers use ``model``, ``charge`` and ``mesh``.
Nothing below ``gui`` imports Qt.

The gui
-------

``gui/`` holds

- ``main_window.ui``, ``settings_dialog.ui``, ``export_dialog.ui``,
  ``coil_params.ui``, ``project_dialog.ui``: the layouts, edited with Qt
  Designer (``pyside6-designer``)
- ``ui_*.py``: generated from the ``.ui`` files, never edited by hand
- ``main_window.py``: the window, connects the widgets to the rest
- ``stimulation.py``: coils and electrodes on the model, snapping, alignment
  and undo
- ``viewport.py``: the 3D view (vedo), and a stand in when there is no OpenGL
- ``plots.py``: embedded matplotlib panels that can pop out
- ``app.py``: starts the window. With ``BEMFMM_READY_FILE`` set it creates
  that file after the first render of the shown window, the run scripts retry
  with ``--no-3d`` when it is missing after a failed start
- ``solve_runner.py``: runs ``bemfmm`` commands in a child process and reads
  their progress
- ``theme.py`` and ``style.qss``: light and dark themes, the stylesheet is a
  template filled from ``theme.COLORS``
- ``settings.py`` and ``dialogs.py``: saved preferences and the dialogs
- ``widgets.py``: custom widgets, used in the ``.ui`` files by promoting a
  standard widget in Qt Designer (``SciSpinBox`` for tolerances)

After editing a ``.ui`` file regenerate its module and format it::

    pyside6-uic src/bemfmm/gui/main_window.ui -o src/bemfmm/gui/ui_main_window.py
    black src/bemfmm/gui/ui_main_window.py

The solver never runs inside the gui process. The gui writes the setup into a
new run folder and starts ``bemfmm tms`` or ``bemfmm tes`` with
``--progress``, which prints lines like ``@progress solve 3 50`` for the
progress bar. Anything the command line can do, the gui can do the same way.

Style
-----

Code is formatted with black and imports sorted with isort, its settings are
in ``pyproject.toml``. ``nix fmt`` runs both, and alejandra on the nix files.
Keep comments for what the code does not
say itself.

Adding a coil generator
-----------------------

A generator is a module in ``coils/generators`` with a function that takes the
coil parameters and builds the wire model and the CAD surface, like
``figure_eight.py``. Register it in ``coils/generators/__init__.py``: the
function in ``GENERATORS``, its parameters with types and defaults in
``COIL_PARAMS`` and its name in ``COIL_TYPES`` to offer it in the gui. It is
then saved in setups by type and parameters and works with
``bemfmm tms --setup``.

Adding a field or a solver
--------------------------

Solvers return a ``Result``. Per facet fields go in ``Result.fields`` and are
saved, exported and shown by the gui without further changes. Add a label and
unit to ``FIELD_LABELS`` in ``results.py`` so the gui lists it. Run information
goes in ``Result.stamp(...)``, which ends up in ``result.json``.

Building these docs
-------------------

::

    cd docs
    sphinx-apidoc -f -o source ../src/bemfmm
    make html
