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

    > requires setup with matplotlib for patches, skipping for now
+ [ ] bemf3_inc_field_electric_dipole.py
    > find elegant solution for line 33
+ [ ] bemf3_inc_field_electric_gauss_selective_dipoles.py
    > requires mesh engine, skipping until, we can define a compatible api
+ [ ] bemf3_inc_field_electric_plain_dipoles.py
    > alot of indexing here, cant be sure until i have something to test on
+ [ ] bemf3_inc_field_electric.py
    > matlabs' implicit field make this ...
+ [ ] bemf4_surface_field_electric_subdiv.py
    > requies mesh_engine, matlab ....
+ [ ] bemf5_volume_field_electric.py
    > matlab ....
+ [ ] potint4b.py almost complete
+ [ ] potint.py matlab ....

+ [ ] bemf1_graphics_electrodes.py -> plot engine
