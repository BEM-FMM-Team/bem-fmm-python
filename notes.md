Brainstorming and discussion from shawn

## Style

[PEP8](https://peps.python.org/pep-0008/) is what we should follow for a consistent python project.
If given permission, I can add git hooks to ensure this is followed.

For now no explicit style guide is to be followed.
But once we have the initial demos out we should obtain one to prevent code smell early.

*Additionally, we should really try to ensure function is typed.*

Classes in python can be problematic but we can see where to integrate them (maybe per engine basis)

Minimize global state, python does not work well with a bunch of global state, unless you want to fight the garbage collector (you can, only in specific casess)

## Future Plans
 - Have structure in python libraries
 - Move all artifacts out of source code directories
 - 3D model rendering should really not be done with matplotlib
 - Threading
 - gpu? (not even sure if possible, i would have to really understand the math for that)

## Resources

I will put things that I found and find are useful here.

> Converting matlab to numpy is not as trivial as it looks. Go line by line.

- np docs - https://numpy.org/doc/stable/user/index.html
- quick ref on converting matlab to numpy - https://mathesaurus.sourceforge.net/matlab-numpy.html

- short ref to matlab syntax -  https://learnxinyminutes.com/matlab/

#### general translations

Careful with np.ndarray.\_\_mul\_\_ and np.matrix.\_\_mul\_\_, the former is always a component wise and the latter is true matrix.
According to numpy, we should generally avoid matrix and do everything with ndarrays,
this means things like matrix multiplication should be explict (leaving `*` for component wise products)


```python
# Source - https://stackoverflow.com/a/26935798
# Posted by Hooked, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-13, License - CC BY-SA 3.0

import numpy as np

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

fig, ax = plt.subplots()
patches = []
num_polygons = 5
num_sides = 5

for i in range(num_polygons):
    polygon = Polygon(np.random.rand(num_sides ,2), True)
    patches.append(polygon)

p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)

colors = 100*np.random.rand(len(patches))
p.set_array(np.array(colors))

ax.add_collection(p)

plt.show()
```
