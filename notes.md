Brainstorming and discussion from shawn

All these use numpy as a backend so we dont have to worry about duplication of memory

 - [trimesh](https://github.com/mikedh/trimesh) - mesh loader
 - [shapely](https://github.com/shapely/shapely) - mesh manipulation
 - [pyglet](https://pyglet.org/) - matplotlib is not going to cut it for large number of vertices


Okay so matplotlib is not going to cut it for a large number of vertices. It just isnt designed for the task.
What I suggest is one of the following (of both, dumping processed can trades storage, which im told we have practically infinite, for cpu time):
 - trimesh rendering with pyglet
 - dumping the raw vertices, faces, normals (for lighting, its also just nice to have normals precomputed) and colors/materials to some obj/stl/...3dmodel file and rendering it with a dedicated program.

## Style

[PEP8](https://peps.python.org/pep-0008/) is what we should follow for a consistent python project.
If given permission, I can add git hooks to ensure this is followed.

For now no explicit style guide is to be followed.
But once we have the initial demos out we should obtain one to prevent code smell early.

*Additionally, we should really try to ensure function is typed.*

Classes in python can be problematic but we can see where to integrate them (maybe per engine basis)

Minimize global state, python does not work well with a bunch of global state, unless you want to fight the garbage collector (you can, only in specific casess)

## Future Plans
 - jupyter notebooks
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
