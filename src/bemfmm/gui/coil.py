import numpy as np
import copy


class Coil:
    def __init__(self):
        # identification information
        self.id = ...
        self.type = ...
        self.name = ...

        # template information
        self.t = ...
        self.cad_template_P = ...
        self.str_template_P = ...

        # wire information
        self.Pwire = ...
        self.Ewire = ...
        self.Swire = ...

        # cad information
        self.cad_P = ...
        self.centerline = np.asarray([[0.0, 0.0, 0.0], [0.0, 0.0, -0.05]])
        self.bottom_to_com = ...  # z delta from coil bottom to center of mass

        # transform information
        self.com = np.zeros(3)
        self.rot = np.array([0.0, 0.0, 0.0, 1.0])  # quaternion
        self.distance = 0  # distance from head
        self.dIdt = 0

        self.Epri = 0

        self.intersection_point = ...

    def clone(self):
        import copy

        return copy.deepcopy(self)
