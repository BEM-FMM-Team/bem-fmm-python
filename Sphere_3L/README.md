# Sphere_3L
Initial test for translations

## Inital notes

```txt
3 Layer (4 shell) sphere model.
Can load meshphere3, which is a sphere of radius 1, and has approximately 3000 vertices.
Inner and Outer conductivities (S/m)

bem functions within this directory are not (currently) in the MatlabEngines01 directory.
fgmres is not in MatlabEngines01, and should not be, since it already has a python equivalent.

cmap_polarity is just a colormap, no need to worry about it too much.
can just use whatever colormaps we want.

Layers : cond_in : cond_out
---------------------------
Skin : 0.465  : 0.0000
Skull: 0.0100 : 0.4650
GM   : 0.2750 : 0.0100
WM   : 0.1260 : 0.2750
```

## Implementation

Nothing is tested as of yet as this is the test itself

- [x] wrapper
    - [x] load_mesh
        - ...
    - [x] charge_engine > everything needed is complete, just the wrapper side
        - [x] surface_field_lhs ../ChargeEngine/bemf4_surface_field_lhs.py
        - [x] surface_field_electric_plain ../ChargeEngine/bemf4_surface_field_electric_plain.py
        - [x] surface_field_potential_accurate ../ChargeEngine/bemf4_surface_field_potential_accurate.py
        - [x] surface_field_electric_accurate ../ChargeEngine/bemf4_surface_field_electric_accurate.py
