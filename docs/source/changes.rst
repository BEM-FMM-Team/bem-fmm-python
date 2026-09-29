Changes
=======

Unreleased
----------

GUI

- The window is explicitly in TMS or tDCS mode. The mode is switched from the
  toolbar or the Mode menu (Ctrl+1, Ctrl+2) and shown in the window title, the
  status bar and the name of the second tab. The run button says what it runs.
  ``bemfmm gui --mode tms|tdcs`` picks the mode at start, otherwise the last
  one used is restored.
- Only the coils or the electrodes of the current mode are shown in the 3D
  view.
- Results are in tabs next to the 3D view: Convergence, Slices, Distribution
  and Electrodes, drawn with matplotlib inside the window. Every plot has the
  matplotlib toolbar (zoom, pan, save) and can be popped out into its own
  window and docked back.
- The Slices tab shows the E-field on the three slice planes. Runs compute the
  slices when "Compute E-field slices" is ticked, older results can compute
  them with the Compute slices button.
- Export fields dialog: chosen fields, all facets or one tissue, mat, npz or
  csv, optionally with the mesh.
- File > Save 3D view image (Snapshot in the toolbar).
- Settings dialog (Edit > Settings): theme (System, Light, Dark), the name of
  the skin tissue, the start mode, the output folder and whether runs compute
  slices. Settings are kept between sessions.
- Dark theme for the whole window, including the 3D view and the plots.
- The Electrodes tab has its own Place on surface. It assumes the skin tissue
  and can be set to any tissue, the electrodes follow it. The Coils tab has its
  own Place on as well.
- Align to (Coils tab) sets the tissue whose normal orients the coil for Auto
  orient, Drag and Aim at. The default is the Place on surface, which keeps the
  previous behavior. With another tissue, for example gm, the coil axis follows
  the gm normal at the target and the coil is moved out along that normal to
  the set distance above the skin.
- Electrodes are drawn as the skin facets the tDCS solver will imprint for
  them, with their edges, instead of a flat disk that cut into curved skin.
  The patch follows the electrode while it is dragged or resized.
- Tolerance in the Solve tab is shown and typed in scientific notation and its
  arrows step by a factor of ten. Values below 1e-10 are no longer rounded to
  zero.
- Fixed: picking an Aim at target and then selecting another coil moved that
  coil to the target. Anything but Place coil now cancels the pick, and the
  status bar names the coil the target is for.
- Fixed: Ctrl+Z after a tissue table edit undid an unrelated coil or electrode
  edit and left the table edited. On the Model tab Undo and Redo now act on the
  table, and a table undone back to the loaded model no longer blocks runs.
- Fixed: switching between TMS and tDCS reset Max iterations and Tolerance to
  their defaults. Each mode now keeps its own values.
- Fixed: electrodes kept the coordinates of the previous model when another
  one was loaded, and the solver then snapped them to whatever skin was
  nearest. They are now moved onto the new surface, and coils whose height
  above their surface changed by more than 5 mm are reported.
- Fixed: a tDCS run with one electrode, or with all electrodes at the same
  voltage, was solved and gave meaningless currents. The gui refuses to run it
  and says why.

Command line

- ``bemfmm slices RESULT [--planes X Y Z]`` computes E-field slices for a saved
  result into ``slices.npz``.
- ``bemfmm tms`` and ``bemfmm tdcs`` take ``--slices``.
- ``bemfmm tdcs --skin`` defaults to the surface stored in the setup.
- ``bemfmm show`` uses saved slices instead of computing them again.

Library

- ``Result.export`` writes fields to mat, npz, csv or pkl files, for all facets
  or one tissue, optionally with the mesh. ``--save-format`` uses it.
- ``electrode.montage_problem`` says why a set of electrodes cannot drive a
  current. ``tdcs.solve`` raises ``ValueError`` with it, and ``bemfmm tdcs``
  checks it before loading the model.
- ``plot.results.compute_slices``, ``plot.slice.draw_efield_slice``,
  ``save_slices`` and ``load_slices``. ``plot_efield_slice`` draws with
  ``draw_efield_slice`` and the tissue outlines are drawn as one collection per
  tissue, which is much faster for large models.
- Setups store ``mode`` and ``skin``. Older setups still open.
- ``electrode.imprint_patch`` imprints one electrode on the facets of a surface
  near it, the same cut as the solver in a few ms.

Run scripts

- ``run.bat`` and ``run.command`` install uv with its official installer when
  it is missing and let uv provide Python 3.13, so no Python has to be
  installed first. Without uv they use an installed Python 3.11 or newer.
- ``.venv`` is set up again when it no longer imports ``bemfmm`` or was
  installed from a different ``pyproject.toml``.
- ``run_no3d.bat`` calls ``run.bat --no-3d``, and ``run_no3d.command`` is new.
- Fixed in ``run.bat``: variables set inside blocks were read before they were
  set, so installing uv through pip never worked and a failed start was
  reported as a success. Falling back from uv to pip reused a venv without pip.
  Errors now keep the window open.
- ``.gitattributes`` keeps ``.bat`` files CRLF, which ``cmd.exe`` needs for
  reliable labels.
- When ``bemfmm gui`` fails before its window and 3D view are up, for example
  on a remote desktop without OpenGL, the run scripts start it again with
  ``--no-3d``. A crash after the window was up is reported, not restarted.

The numerics of all solvers are unchanged.

Refactor
--------

The previous round moved everything into the ``bemfmm`` package with one
command, a new gui built from ``.ui`` files, the solver classes in
``bemfmm.solvers``, result folders, setups as json, the three layer sphere as a
tissue index, tests and a benchmark. See the git history for details.
