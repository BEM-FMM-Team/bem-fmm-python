import numpy as np

from bemfmm.gui.field_display import (
    AUTO_COLOR_PERCENTILES,
    charge_density_display_scale,
    percentile_color_limits,
)


def test_charge_density_display_scale_uses_prefix_for_magnitude():
    scale, unit = charge_density_display_scale(np.array([-2e-10, 5e-10]))

    assert scale == 1e12
    assert unit == "pC/m^2"


def test_charge_density_display_scale_keeps_zero_in_base_units():
    scale, unit = charge_density_display_scale(np.zeros(3))

    assert scale == 1
    assert unit == "C/m^2"


def test_percentile_color_limits_use_requested_percentiles():
    low, high = percentile_color_limits(np.arange(100), 5, 95)

    np.testing.assert_allclose([low, high], [4.95, 94.05])


def test_auto_color_limits_use_half_and_ninety_nine_and_a_half_percentiles():
    low, high = percentile_color_limits(np.arange(100), *AUTO_COLOR_PERCENTILES)

    np.testing.assert_allclose([low, high], [0.495, 98.505])


def test_manual_percentile_color_limits():
    low, high = percentile_color_limits(np.arange(100), 10, 90)

    np.testing.assert_allclose([low, high], [9.9, 89.1])
