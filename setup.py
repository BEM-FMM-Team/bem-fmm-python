import sys

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

if sys.platform == "win32":
    compile_args = ["/O2", "/openmp"]
    link_args = ["/openmp"]
elif sys.platform == "linux":
    compile_args = ["-O3", "-fopenmp"]
    link_args = ["-fopenmp"]
else:  # TODO macos
    compile_args = ["-O3", "-fopenmp"]
    link_args = ["-fopenmp"]


extensions = [
    Extension(
        name="neighbor_ints",
        sources=[
            "_neighbor_ints/neighbor_ints_Enpyx.pyx",
            "_neighbor_ints/neighbor_ints_En.c",
        ],
        include_dirs=[
            np.get_include(),
            "_neighbor_ints",
        ],
        extra_compile_args=compile_args,
        extra_link_args=link_args,
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        language_level="3",
        include_path=[
            "_neighbor_ints",
        ],
    ),
)
