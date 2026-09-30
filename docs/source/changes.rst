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
- Coils and electrodes are selected by clicking them in the 3D view. Clicking
  empty space in the view or the list, or Esc, clears the selection, so
  nothing has to stay highlighted.
- Show in 3D view keeps its state when switching tabs instead of being turned
  off outside the Results tab. The result stays in the view on the Model and
  Solve tabs and steps aside only on the Coils/Electrodes tab.
- Twist is read from the coil pose, so the box no longer jumps back to 0 after
  another edit, and changing Distance, Auto orient, dragging and Aim at keep the
  twist instead of resetting the coil to its default turn about the axis.
- The slices use ``viridis`` instead of ``jet``, and the Slices tab has a
  Colormap choice (viridis, plasma, inferno, cividis, hot, jet).
- Results open on the tissue picked last, ``gm`` at first, for TMS and tDCS
  alike (TMS results used to open on ``wm``).
- Coils and electrodes are moved by pressing on them in the 3D view, moving
  the mouse and releasing. The Drag buttons, which picked an item up on one
  click and dropped it on the next, are gone. Dragging on empty space still
  turns the camera.
- Delete or Backspace removes the selected coil or electrode from anywhere on
  the Coils/Electrodes tab or after a click in the 3D view, not only while
  its list has focus.
- Tolerance in the Solve tab is shown and typed in scientific notation and its
  arrows step by a factor of ten. Values below 1e-10 are no longer rounded to
  zero.
- Slices can be on any list of planes instead of the three axis planes, set
  by a normal and a position (the plane y = x is normal ``1, -1, 0``). The
  default is still the planes through the origin normal to x, y and z.
- The planes have their own Planes tab next to the 3D view: a list of planes,
  orientation buttons, a position slider, a plane through a picked point, and
  an arrow on the selected plane in the 3D view that drags it along its
  normal. The tab says when the computed slices no longer match the planes.
- Saving a setup while the model comes from applied but unsaved tissue edits
  offers to save the tissue index first, so the setup can point to it. It
  used to show the same notice on every save and write no tissue index.
- Fixed: closing the window, New and Open only asked to save when there were
  coils or electrodes, so slice plane changes were lost. They now ask when the
  coils, electrodes or planes differ from the saved setup, and not after
  undoing back to it.
- The Plot windows button in the Results tab is now Open in separate windows,
  since the same plots are in the tabs next to the 3D view.
- The gui shows plain names instead of variable names. Coil parameters have
  labels and are in mm, the cross-section shape (``flag``) and the current
  distribution (``sk``) are picked from lists, coil types have readable names,
  and the exported fields read E-field, Charge and so on instead of ``E`` and
  ``c``. The file names of exported fields are unchanged.
- Show coils (Show electrodes) in the Results tab hides them over a result
  without removing them from the setup.
- Fixed: a tDCS result stayed in the Results tab and the 3D view after
  switching to TMS, and the other way round. Each mode now keeps its own last
  result.
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

- tDCS integrates the potential on the electrodes exactly over the nearest 512
  facets instead of 32 (``--num-neighbors-p``, Potential integrals in the
  gui).
- ``bemfmm slices RESULT [--planes X Y Z] [--plane NX,NY,NZ,PX,PY,PZ ...]``
  computes E-field slices for a saved result into ``slices.npz``.
- ``bemfmm tms`` and ``bemfmm tdcs`` take ``--slices``.
- ``bemfmm tdcs --skin`` defaults to the surface stored in the setup.
- ``bemfmm show`` uses saved slices instead of computing them again.

Library

- ``Result.export`` writes fields to mat, npz, csv or pkl files, for all facets
  or one tissue, optionally with the mesh. ``--save-format`` uses it.
- ``coils.rotation.axis_twist`` splits a coil pose into its axis and the twist
  about it, ``twisted`` builds it back. ``Stimulation.twist_coil`` takes the
  twist alone.
- ``electrode.montage_problem`` says why a set of electrodes cannot drive a
  current. ``tdcs.solve`` raises ``ValueError`` with it, and ``bemfmm tdcs``
  checks it before loading the model.
- ``plot.results.compute_slices``, ``plot.slice.draw_efield_slice``,
  ``save_slices`` and ``load_slices``. ``plot_efield_slice`` draws with
  ``draw_efield_slice`` and the tissue outlines are drawn as one collection per
  tissue, which is much faster for large models.
- Setups store ``mode`` and ``skin``. Older setups still open.
- ``bemfmm.planes.Plane`` is a slice plane by its normal and a point.
  ``compute_slices`` takes a list of them and returns a list of slices,
  ``compute_efield_overlay`` takes one, and setups store them (version 2).
  ``slices.npz`` stores any number of planes, older files still load.
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
