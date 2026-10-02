from pathlib import Path

from PySide6.QtCore import QSettings

START_MODES = ["last", "tms", "tdcs"]
RECENT_PROJECTS = 8


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
        "project": "",
        "recent_projects": "",
        "ask_project": True,
    }

    def __init__(self):
        self.store = QSettings("WPI", "BEM-FMM")

    def __getitem__(self, key):
        default = self.DEFAULTS[key]
        return self.store.value(key, default, type=type(default))

    def __setitem__(self, key, value):
        self.store.setValue(key, value)

    def recent_projects(self):
        # newest first, one folder per line
        return [p for p in self["recent_projects"].split("\n") if p]

    def add_recent_project(self, folder):
        folder = str(folder)
        recent = [folder] + [p for p in self.recent_projects() if p != folder]
        self["recent_projects"] = "\n".join(recent[:RECENT_PROJECTS])
        self["project"] = folder

    def output_dir(self):
        return self["output_dir"] or str(Path.cwd() / "__output__")
