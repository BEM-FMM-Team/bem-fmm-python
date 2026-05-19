# Charge Engine

Starting with trival conversions, skipping involved translations

`lib.py` and `test.py` are temporary

Nothing is tested, just initial translations

The non-trivial translations may require more inspection hence will be slower to get done.

+ [ ] bemf1_graphics_electrodes.py
    > non-trivial, requires setup with matplotlib for patches,  skipping for now
+ [x] bemf3_inc_field_electric_constant.py
+ [ ] bemf3_inc_field_electric_dipole.py
    > find elegant solution for line 33
+ [ ] bemf3_inc_field_electric_gauss_selective_dipoles.py
    > non-trivial, requires mesh engine, skipping until, we can define a compatible api
+ [ ] bemf3_inc_field_electric_plain_dipoles.py
    > non-trivial, alot of indexing here
+ [ ] bemf3_inc_field_electric.py
    > non-trivial, matlabs' implicit field make this ...
+ [x] bemf4_electrode_current.py
+ [x] bemf4_surface_field_electric_accurate.py
+ [x] bemf4_surface_field_electric_plain.py
+ [ ] bemf4_surface_field_electric_subdiv.py
    > non-trivial, requies mesh_engine, matlab ....
+ [x] bemf4_surface_field_lhs_i.py
+ [x] bemf4_surface_field_lhs.py
+ [x] bemf4_surface_field_lhs_v.py
+ [x] bemf4_surface_field_lhs_v_v2.py
+ [ ] bemf5_volume_field_electric.py
    > non-trivial, matlab ....
+ [ ] potint4b.py
    > non-trivial, almost complete
+ [ ] potint.py
    > non-trivial, matlab ....
+ [x] bemf4_surface_field_potential_accurate.py
