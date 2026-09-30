Getting started
===============

Install
-------

The run scripts in the repository root set everything up the first time they
are started. They install `uv <https://docs.astral.sh/uv/>`_ and Python 3.13
when they are missing, and use an installed Python 3.11 or newer when that
fails. Python 3.11 to 3.14 are supported:

- Windows: ``run.bat`` (double click it or start it from a terminal).
- Linux and MacOS: ``run.command``.

``run_no3d.bat`` and ``run_no3d.command`` open the same program without the 3D
view, for remote desktop sessions without a usable OpenGL driver. When the
window does not open with the 3D view, ``run.bat`` and ``run.command`` start
it again without it. Arguments are passed on to ``bemfmm gui``, for example
``run.bat --mode tdcs``.

The environment is kept in ``.venv`` and set up again when ``pyproject.toml``
changed, for example after a ``git pull`` that changed the dependencies. To
start over, delete ``.venv``.

To install by hand, in the repository root::

    python -m pip install uv
    python -m uv venv
    .venv\Scripts\activate          (Windows)
    source .venv/bin/activate       (Linux, MacOS)
    python -m uv pip install -e .

This puts the ``bemfmm`` command on the path. ``python -m bemfmm`` does the
same thing.

A first TMS run
---------------

1. Start the program with ``bemfmm gui --mode tms``. The default head model
   loads, and the window title and the status bar both say ``TMS``.
2. Open the **Coils** tab, pick ``figure_eight`` and press **Add coil**. Accept
   the generator parameters.
3. Set **Aim at** to ``gm``, press **Pick target**, click a point on the gray
   matter in the 3D view and press **Place coil**. The coil sits 10 mm above
   the skin, over that point.
4. Press **Run TMS** in the toolbar (or F5). The Solve tab shows progress and
   the solver log.
5. When the run finishes the Results tab opens. The 3D view shows the E-field on
   the chosen tissue, and the Convergence and Slices tabs next to
   the 3D view show the rest.

A first tDCS run
----------------

1. Switch to tDCS with the **tDCS** button in the toolbar (or Ctrl+2). The
   second tab becomes **Electrodes**.
2. Press **Add electrode** twice. New electrodes alternate between +1 V and
   -1 V. Type a position for each one, it snaps to the skin.
3. Press **Run tDCS**. The Results tab lists the solved voltage and current of
   every electrode, and the Electrodes tab next to the 3D view plots the
   currents.

Where results go
----------------

Every run gets its own folder, ``tms-<date>-<time>`` or ``tdcs-<date>-<time>``,
inside the output folder (``__output__`` in the folder the program was started
from, unless changed in Settings). The folder holds the setup that was solved,
the result files and, if they were computed, the E-field slices. Open an older
run with File > Open result.

Trying things on the sphere
---------------------------

The three layer sphere in ``src/bemfmm/assets/sphere_3L`` solves in seconds and
is the quickest way to try settings::

    bemfmm gui --tissue-index src/bemfmm/assets/sphere_3L/tissue_index.yaml
