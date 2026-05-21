# Charge Engine

Starting with trival conversions, skipping involved translations

`lib.py` and `test.py` are temporary

Nothing is tested, just initial translations

The non-trivial translations may require more inspection hence will be slower to get done.

+ [x] bemf4_surface_field_lhs_v_v2.py
+ [x] bemf4_surface_field_lhs_i.py
+ [x] bemf4_surface_field_lhs.py
+ [x] bemf4_surface_field_lhs_v.py
+ [x] bemf4_surface_field_potential_accurate.py
+ [x] bemf4_electrode_current.py
+ [x] bemf4_surface_field_electric_accurate.py
+ [x] bemf4_surface_field_electric_plain.py
+ [x] bemf3_inc_field_electric_constant.py

+ [ ] bemf3_inc_field_electric_dipole.py
    > potint2 function ?
+ [ ] bemf3_inc_field_electric_gauss_selective_dipoles.py
    > mesh_tri function ?
+ [ ] bemf3_inc_field_electric_plain_dipoles.py
    > CONFIRM intent on line 43, 52
    > alot of indexing here, cant be sure until i have something to test on
+ [ ] bemf3_inc_field_electric.py
    > CONFIRM line 16 indexing
+ [ ] bemf4_surface_field_electric_subdiv.py
    > mesh_tri function ?
+ [ ] bemf5_volume_field_electric.py
    > norm, rangesearch ?
+ [ ] potint4b.py
    > struggle with 3d repmat
+ [ ] potint.py
    > complete but i am uncertain that it and matlab compute the same

+ bemf1_graphics_electrodes.py -> plot engine has same function ../plot/bemf1_graphics_electrodes.py
