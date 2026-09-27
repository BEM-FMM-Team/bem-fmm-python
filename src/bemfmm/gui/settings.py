from pathlib import Path

from PySide6.QtCore import QSettings

START_MODES = ["last", "tms", "tdcs"]


class Settings:
    """
    Preferences kept between sessions. An empty output folder means __output__
    in the folder the gui was started from
    """

    DEFAULTS = {
        "theme": "system",
        "skin": "skin",
        "start_mode": "last",
        "mode": "tms",
        "output_dir": "",
        "slices": True,
    }

    def __init__(self):
        self.store = QSettings("WPI", "BEM-FMM")

    def __getitem__(self, key):
        default = self.DEFAULTS[key]
        return self.store.value(key, default, type=type(default))

    def __setitem__(self, key, value):
        self.store.setValue(key, value)

    def output_dir(self):
        return self["output_dir"] or str(Path.cwd() / "__output__")
