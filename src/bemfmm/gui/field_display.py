import numpy as np


def charge_density_display_scale(values):
    prefixes = {
        -24: "y",
        -21: "z",
        -18: "a",
        -15: "f",
        -12: "p",
        -9: "n",
        -6: "µ",
        -3: "m",
        0: "",
        3: "k",
        6: "M",
        9: "G",
        12: "T",
        15: "P",
        18: "E",
        21: "Z",
        24: "Y",
    }
    values = np.asarray(values)
    finite = np.abs(values[np.isfinite(values)])
    magnitude = np.max(finite, initial=0.0)
    exponent = 0
    if magnitude:
        exponent = int(np.clip(3 * np.floor(np.log10(magnitude) / 3), -24, 24))
    return 10.0 ** -exponent, f"{prefixes[exponent]}C/m^2"


def auto_color_limits(values):
    # percentile limits are more robust to outliers than min/max
    return np.percentile(values, [5, 95])
