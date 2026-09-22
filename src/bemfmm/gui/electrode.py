import copy

import numpy as np


class Electrode:
    def __init__(self):
        # identification information
        self.id = ...
        self.name = ...

        # placement information, always sits on the skin surface
        self.center = np.zeros(3)
        self.normal = np.array([0.0, 0.0, 1.0])
        self.faceIdx = ...

        # disk mesh built from center/normal/radius, used for rendering
        self.disk_P = ...
        self.disk_t = ...

        # electrode parameters
        self.radius = 0.005  # m
        self.voltage = 0.0  # V

    def clone(self):
        return copy.deepcopy(self)
