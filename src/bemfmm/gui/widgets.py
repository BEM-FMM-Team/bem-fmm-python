import re

from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QDoubleSpinBox

PARTIAL_NUMBER = re.compile(r"\+?\d*\.?\d*(e[+-]?\d*)?", re.IGNORECASE)


class SciSpinBox(QDoubleSpinBox):
    """
    Double spin box shown in scientific notation, 1e-4 or 2.5e-6. Each arrow
    step multiplies or divides by ten, page up and down by ten steps. Used for
    tolerances, set it up in Qt Designer by promoting a QDoubleSpinBox
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # qt rounds every value to this many decimals, 323 keeps all of them
        self.setDecimals(323)

    def textFromValue(self, value):
        mantissa, exponent = f"{value:.3e}".split("e")
        mantissa = mantissa.rstrip("0").rstrip(".")
        return f"{mantissa}e{int(exponent)}"

    def valueFromText(self, text):
        return float(text)

    def validate(self, text, pos):
        try:
            value = float(text)
        except ValueError:
            if PARTIAL_NUMBER.fullmatch(text):
                return QValidator.State.Intermediate
            return QValidator.State.Invalid
        if self.minimum() <= value <= self.maximum():
            return QValidator.State.Acceptable
        return QValidator.State.Intermediate

    def stepBy(self, steps):
        self.setValue(self.value() * 10.0**steps)
