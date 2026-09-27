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

Command line

- ``bemfmm slices RESULT [--planes X Y Z]`` computes E-field slices for a saved
  result into ``slices.npz``.
- ``bemfmm tms`` and ``bemfmm tdcs`` take ``--slices``.
- ``bemfmm tdcs --skin`` defaults to the surface stored in the setup.
- ``bemfmm show`` uses saved slices instead of computing them again.

Library

- ``Result.export`` writes fields to mat, npz, csv or pkl files, for all facets
  or one tissue, optionally with the mesh. ``--save-format`` uses it.
- ``plot.results.compute_slices``, ``plot.slice.draw_efield_slice``,
  ``save_slices`` and ``load_slices``. ``plot_efield_slice`` draws with
  ``draw_efield_slice`` and the tissue outlines are drawn as one collection per
  tissue, which is much faster for large models.
- Setups store ``mode`` and ``skin``. Older setups still open.

The numerics of all solvers are unchanged.

Refactor
--------

The previous round moved everything into the ``bemfmm`` package with one
command, a new gui built from ``.ui`` files, the solver classes in
``bemfmm.solvers``, result folders, setups as json, the three layer sphere as a
tissue index, tests and a benchmark. See the git history for details.
