The graphical interface
=======================

Start it with ``bemfmm gui``. Options::

    bemfmm gui --mode tdcs                          start in tDCS mode
    bemfmm gui --tissue-index my_model/tissue_index.yaml
    bemfmm gui --setup study/setup.json             open a saved setup
    bemfmm gui --no-3d                              no 3D view, for remote desktops

The window has a side panel with four tabs on the left and the result views on
the right.

TMS or tDCS
-----------

The program is always in one of two modes, and the mode is shown in four
places: the two buttons at the left of the toolbar, the window title, the badge
in the status bar and the name of the second tab (**Coils** or **Electrodes**).
The run button says **Run TMS** or **Run tDCS**.

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
- the coil generators (``figure_eight``, ``ring``, MagVenture models and
  others), each with its own parameters
- ``template: <name>`` for the templates in ``src/bemfmm/coils/templates``,
  and **Template file...** for any other strcoil ``.mat`` file

The list holds the coils of the setup. Double click to rename, Delete removes
the selected one.

**Selected coil**

- **Position** (mm) and **Rotation** (degrees, x y z) of the coil center
- **Twist**: rotation about the coil axis
- **Distance**: from the bottom of the coil to the surface, in mm
- **dI/dt** in A/us
- **Auto orient**: points the axis along the Align to normal
- **Flip**: turns the coil over
- **Drag**: press it, click the coil in the 3D view, move the mouse over the
  surface, click again to drop it
- **Aim at**: pick a tissue, press **Pick target**, click a point on that
  tissue and press **Place coil**. The coil goes the set distance above the
  Place on surface, oriented as described under Align to

Electrodes tab (tDCS)
---------------------

- **Place on**: the surface the electrodes are imprinted on, where current
  enters and leaves the head. It assumes the skin tissue (``skin``, or the name
  set in Settings) and can be changed to any tissue. Changing it moves the
  existing electrodes onto the new surface.
- **Add electrode** adds a disk electrode. New ones alternate between +1 V
  and -1 V. The 3D view draws the skin facets the solver will imprint for it,
  so on curved or folded skin it shows the exact patch that carries current.
- **Selected electrode**: position (snapped to the surface), radius in mm and
  voltage. **Drag** moves it in the 3D view like a coil.

Anodes are drawn red, cathodes blue, the selected item cyan.

Slice planes
------------

The x, y and z positions (mm) of the three planes used for the E-field slices.
**Show** draws them in the 3D view.

Solve tab
---------

Solver settings:

- **Neighbor integrals**: nearest facets integrated exactly for the E-field (4)
- **Potential integrals**: tDCS only, nearest facets integrated exactly for the
  potential on the electrodes (32)
- **Max iterations** and **Tolerance**: when GMRES stops. The defaults are
  20 and 1e-4 for TMS, 50 and 1e-6 for tDCS. Tolerance is typed and shown in
  scientific notation (``1e-6``, ``2.5e-7``), the arrows step by a factor of
  ten
- **Conservation weight**: weight of the term that keeps the total charge
  (TMS) or the total electrode current (tDCS) at zero

Output:

- **Folder** where the run folders are made
- **Also export** writes the ticked fields as ``mat``, ``npz``, ``csv`` or
  ``pkl`` files next to the result
- **Compute E-field slices** also computes the slices after the solve

The solver runs in a separate process, so the window stays responsive and a
crash in the solver cannot close it. **Cancel** stops the run.

Results tab
-----------

Shows the run (type, model, date, convergence and folder) and controls what the
3D view shows:

- **Field** and **Tissue**: any stored field on any tissue
- **Colormap** and **Range** (automatic or fixed)
- the minimum, median, 99th percentile and maximum of the values shown
- **Show in 3D view** switches between the result and the setup

For tDCS results the table lists the set and solved voltage and the current of
every electrode, with the current balance (should be close to zero) and the
power.

**Export fields...** writes chosen fields, for all facets or one tissue, as
``mat``, ``npz`` or ``csv``, optionally with the mesh. **Plot windows** opens
the separate plot windows of ``bemfmm show``. **Open folder** opens the run
folder.

Result views
------------

The tabs on the right:

- **3D view**: the model, coils, electrodes and the field on a tissue.
  **Snapshot** in the toolbar (File > Save 3D view image) saves it as an image.
- **Convergence**: relative residual per GMRES iteration, with the tolerance.
- **Slices**: the total E-field on the three slice planes with the tissue
  outlines, one plane or all three. **Compute slices** computes them for the
  current slice planes if the run did not.
- **Distribution**: histogram of the field and tissue picked in the Results
  tab, with the median and 99th percentile.
- **Electrodes**: tDCS only, the current of every electrode.

Every plot has the matplotlib toolbar: home, back and forward, pan, zoom,
subplot spacing, axis settings and save (png, pdf, svg and more). **Pop out**
moves the plot into its own window, which can be resized or put on a second
screen. Closing that window, or pressing **Dock**, puts it back.

3D view mouse and keys
----------------------

========================= ==================================
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
electrodes and planes.

Settings
--------

Edit > Settings (Ctrl+,):

- **Theme**: System, Light or Dark. System follows the desktop and changes
  with it.
- **Skin tissue**: the name of the scalp surface in your tissue indexes, used
  as the default Place on surface. ``skin`` unless your models call it
  something else.
- **Start in**: the last used mode, TMS or tDCS.
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
3D view still works, including all result plots.
