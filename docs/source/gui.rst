The graphical interface
=======================

Start it with ``bemfmm gui``. Options::

    bemfmm gui --mode tes                           start in TES mode
    bemfmm gui --tissue-index my_model/tissue_index.yaml
    bemfmm gui --setup study/setup.json             open a saved setup
    bemfmm gui --no-3d                              no 3D view, for remote desktops

The window has a side panel with four tabs on the left and the result views on
the right.

TMS or TES
-----------

The program is always in one of two modes, and the mode is shown in four
places: the two buttons at the left of the toolbar, the window title, the badge
in the status bar and the name of the second tab (**Coils** or **Electrodes**).
The run button says **Run TMS** or **Run TES**.

Switch with the toolbar buttons, the Mode menu, or Ctrl+1 and Ctrl+2. Coils and
electrodes are both kept while switching. Only the ones of the current mode are
shown and only those are solved. Without ``--mode`` the program starts in the
mode used last, which Settings can change.

Model tab
---------

Opens a tissue index and shows it as a table:

- **Tissue**: the name, double click to rename it. Other rows that point at it
  follow the new name.
- **S/m**: conductivity inside the surface.
- **Outside**: the tissue just outside the surface, ``FreeSpace`` for air.
- **Mesh file**: the surface mesh (``.stl``, ``.obj``, ``.ply`` or ``.vtk``, in mm).

**Add** reads more surfaces, **Remove** deletes the selected row (whatever was
inside it moves to its outside). **Apply** checks the table and reloads the
model with it, **Save as** writes it to a new tissue index. A run with applied
but unsaved edits writes the edited index into the run folder, so the run can
always be repeated.

While the Model tab is open, Undo and Redo step through the table edits. Undoing
back to the loaded model clears the edited state, so Apply is not needed.

When another model is loaded, electrodes are moved onto its surface (one undo
step). Coils keep their pose, and a message lists every coil whose height above
its surface changed by more than 5 mm.

**Display** turns tissues on and off in the 3D view and sets their opacity.

Coils tab (TMS)
---------------

**Placement**

- **Place on**: the surface coils sit above and are dragged over. The skin
  tissue by default.
- **Align to**: the tissue whose surface normal sets the coil axis. It starts
  on the same tissue as Place on, which points the coil along the skin normal.
  Picking another tissue, for example ``gm``, points the coil along the normal
  of that tissue instead. The coil is then moved along that normal until it is
  the set distance above the Place on surface.

**Adding coils**: pick a type and press **Add coil**. The types are

- ``default (bundled coil)``: the coil and pose used by ``bemfmm tms``
  without a setup
- the coil generators (Ring, Figure-eight, MagVenture models and others).
  Adding one opens its parameters: sizes in mm, the number of edges the wire
  is modeled with, the **Wire cross-section** (elliptical or rectangular) and
  the **Current distribution** (skin effect, the current near the wire
  surface, or uniform as in Litz wire). Hover over a parameter for what it
  sets
- ``template: <name>`` for the templates in ``src/bemfmm/coils/templates``,
  and **Template file...** for any other strcoil ``.mat`` file

The list holds the coils of the setup. Double click to rename. Delete (or
Backspace) removes the selected one while this tab is open or after a click in
the 3D view. Clicking a coil in the 3D view selects it, clicking empty
space in the view or the list, or pressing Esc, clears the selection.

**Selected coil**

- **Position** (mm) and **Rotation** (degrees, x y z) of the coil center
- **Twist**: rotation about the coil axis, in degrees. It is part of the pose,
  so moving the coil, changing Distance, Auto orient, dragging and Aim at keep
  it
- **Distance**: from the bottom of the coil to the surface, in mm
- **dI/dt** in A/us
- **Auto orient**: points the axis along the Align to normal, keeping the twist
- **Flip**: turns the coil over
- **Dragging**: press on the coil in the 3D view, move the mouse and release.
  The coil follows the Place on surface under the mouse, the same way Aim at
  and Auto orient place it
- **Aim at**: pick a tissue, press **Pick target**, click a point on that
  tissue and press **Place coil**. The coil goes the set distance above the
  Place on surface, oriented as described under Align to. Selecting another
  coil, undo or switching mode before **Place coil** cancels the pick

Electrodes tab (TES)
---------------------

- **Place on**: the surface the electrodes are imprinted on, where current
  enters and leaves the head. It assumes the skin tissue (``skin``, or the name
  set in Settings) and can be changed to any tissue. Changing it moves the
  existing electrodes onto the new surface.
- **Add electrode** adds a disk electrode. New ones alternate between +1 V
  and -1 V. The 3D view draws the skin facets the solver will imprint for it,
  so on curved or folded skin it shows the exact patch that carries current.
- **Selected electrode**: position (snapped to the surface), radius in mm and
  voltage. Drag it in the 3D view like a coil.

A run needs at least two electrodes at different voltages, the current enters
through some and leaves through the others. The Solve tab says what is missing
and Run refuses until it is fixed.

Anodes are drawn red, cathodes blue, the selected item cyan. Electrodes are
selected and deselected in the 3D view the same way as coils.

Planes tab
----------

The slice planes, next to the 3D view, which switches to show them. By default
they are the planes through the origin normal to x, y and z.

- The list names every plane, for example ``XY at z = 20.0 mm``. The selected
  plane is drawn cyan, the others grey.
- **Add** copies the selected plane, **Remove** (or Delete) removes it and
  **Defaults** puts back the three axis planes through the center of the model.
- **Orientation** turns the selected plane normal to x, y or z.
- **Normal** is the plane's normal, of any length, so ``1, -1, 0`` is the plane
  y = x.
- **Position** moves the plane along its normal: drag the slider across the
  model or type the signed distance from the origin in mm.
- **Through a picked point**: click a point on a surface in the 3D view to put
  the plane through it. Esc cancels.
- In the 3D view the selected plane has an arrow at its edge. Drag the arrow to
  move the plane along its normal. Dragging anywhere else turns the camera.

A plane normal to an axis is plotted in the other two world coordinates, any
other plane in in-plane coordinates u (horizontal) and v (up where the plane
allows). Undo and Redo include the planes, a slider or arrow drag is one step,
and the planes are saved with the setup. When the planes no longer match the
computed slices the tab says so, and **Compute slices** here or in the Slices
view brings them up to date. **Show the planes on the other tabs** keeps them in
the 3D view after leaving the tab.

Solve tab
---------

Solver settings:

- **Preset** fills in the settings below:

  ========= ========================== ==================================
  Preset    TMS                        TES
  ========= ========================== ==================================
  Default   4, 20 iterations, 1e-4     4, 512, 50 iterations, 1e-6
  Accurate  64, 50 iterations, 1e-6    64, 512, 50 iterations, 1e-6
  Fast      4, 20 iterations, 1e-3     4, 32, 20 iterations, 1e-3
  ========= ========================== ==================================

  The numbers are the neighbor integrals, the potential integrals (TES),
  the max iterations and the tolerance. Default is what the command line
  uses, Fast is for benchmarking and quick checks. Changing any of them
  shows **Custom**.
- **Neighbor integrals**: nearest facets integrated exactly for the E-field (4)
- **Potential integrals**: TES only, nearest facets integrated exactly for the
  potential on the electrodes (512)
- **Max iterations** and **Tolerance**: when GMRES stops. The defaults are
  20 and 1e-4 for TMS, 50 and 1e-6 for TES. Each mode keeps its own
  settings while switching. Tolerance is typed and shown in
  scientific notation (``1e-6``, ``2.5e-7``), the arrows step by a factor of
  ten
- **Conservation weight**: weight of the term that keeps the total charge
  (TMS) or the total electrode current (TES) at zero

Output:

- **Folder** where the run folders are made
- **Also export** writes the ticked quantities as ``mat``, ``npz``, ``csv`` or
  ``pkl`` files next to the result
- **Compute E-field slices** also computes the slices after the solve

The solver runs in a separate process, so the window stays responsive and a
crash in the solver cannot close it. **Cancel** stops the run.

Results tab
-----------

Shows the run (type, model, date, convergence and folder) and controls what the
3D view shows. Each mode keeps its own last result: switching between TMS and
TES shows that mode's result, or none, and opening a TMS or TES result
switches to its mode.

- **Quantity** and **Tissue**: any stored quantity (E-field, normal E-field,
  normal current density, charge, potential) on any tissue. Results open on
  the tissue picked last, ``gm`` at first
- **Colormap** and **Range** (automatic or fixed)
- the minimum, median, 99th percentile and maximum of the values shown
- **Show in 3D view** switches between the result and the setup. It is ticked
  for every new result and keeps its state when switching tabs. On the
  Coils/Electrodes tab the view always shows the setup, since placing needs
  the surfaces the result hides
- **Show coils** (**Show electrodes** in TES mode) draws them over the
  result. Untick it to see the solution under them, they are always shown while
  placing

For TES results the table lists the set and solved voltage and the current of
every electrode, with the current balance (should be close to zero) and the
power.

**Export results...** writes chosen quantities, for all facets or one tissue, as
``mat``, ``npz`` or ``csv``, optionally with the mesh. **Open in separate
windows** opens the result in the plot windows of ``bemfmm show``, outside the
main window. They show the same plots as the result tabs, which can also be
popped out one by one. **Open folder** opens the run folder.

Result views
------------

The tabs on the right:

- **3D view**: the model, coils, electrodes and a quantity on a tissue.
  **Snapshot** in the toolbar (File > Save 3D view image) saves it as an image.
- **Convergence**: relative residual per GMRES iteration, with the tolerance.
- **Slices**: the total E-field on the slice planes with the tissue outlines,
  one plane or all of them. **Compute slices** computes them for the planes set
  in the Planes tab, when the run did not or after the planes were changed.
  **Colormap** picks the colors, ``viridis`` by default
- **Electrodes**: TES only, the current of every electrode.

Every plot has the matplotlib toolbar: home, back and forward, pan, zoom,
subplot spacing, axis settings and save (png, pdf, svg and more). **Pop out**
moves the plot into its own window, which can be resized or put on a second
screen. Closing that window, or pressing **Dock**, puts it back.

3D view mouse and keys
----------------------

========================= ==================================
Left click                select a coil or electrode, empty space clears
Drag a coil or electrode  move it over the surface
Esc                       leave Pick target, else clear the selection
Delete, Backspace         remove the selected coil or electrode
Left drag                 rotate
Shift + left drag         pan
Right drag or scroll      zoom
r                         reset the camera
w, s                      wireframe, surface
f                         fly to the point under the mouse
========================= ==================================

The XY, XZ, YZ and Reset buttons in the toolbar set the camera.

Setups
------

File > Save setup writes a ``.json`` file with the coils, electrodes, slice
planes, the mode, the Place on surface and the tissue index. Opening it restores
all of these. Undo and Redo (Ctrl+Z, Ctrl+Shift+Z) cover every change to coils,
electrodes and planes, and on the Model tab the tissue table.

The setup points to the tissue index of the model in use. When that model was
built from applied tissue edits that are in no file, saving the setup offers
**Save tissue index...** first, next to the setup by default, so the setup can
point to it. **Save setup only** saves it without a tissue index. Edits in the
tissue table that were not applied are not part of the model, so they are not
saved with the setup.

New, Open and closing the window ask to save when the coils, electrodes or
planes differ from the saved setup. Undoing back to the saved setup does not
count as a change.

Settings
--------

Edit > Settings (Ctrl+,):

- **Theme**: System, Light or Dark. System follows the desktop and changes
  with it.
- **Skin tissue**: the name of the scalp surface in your tissue indexes, used
  as the default Place on surface. ``skin`` unless your models call it
  something else.
- **Start in**: the last used mode, TMS or TES.
- **Output folder**: where run folders are made, ``__output__`` in the
  working folder when empty.
- **Compute E-field slices after each run**: the default for the checkbox in
  the Solve tab. The slices add from a few seconds (sphere) to about a minute
  (full head) to a run.

Remote desktops
---------------

The 3D view needs OpenGL, which remote desktop sessions often do not have. On a
Windows server with a GPU, enable the group policy "Use hardware graphics
adapters for all Remote Desktop Services sessions". Otherwise start with
``--no-3d`` (``run_no3d.bat``). Everything except dragging and picking in the
3D view still works, including all result plots. ``run.bat`` and
``run.command`` do this by themselves when the window fails to open.
