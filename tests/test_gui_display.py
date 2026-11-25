import numpy as np

from bemfmm.gui.field_display import auto_color_limits, charge_density_display_scale


def test_charge_density_display_scale_uses_prefix_for_magnitude():
    scale, unit = charge_density_display_scale(np.array([-2e-10, 5e-10]))

    assert scale == 1e12
    assert unit == "pC/m^2"


def test_charge_density_display_scale_keeps_zero_in_base_units():
    scale, unit = charge_density_display_scale(np.zeros(3))

    assert scale == 1
    assert unit == "C/m^2"


def test_auto_color_limits_use_fifth_and_ninety_fifth_percentiles():
    low, high = auto_color_limits(np.arange(100))

    np.testing.assert_allclose([low, high], [4.95, 94.05])
