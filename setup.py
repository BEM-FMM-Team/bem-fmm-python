import sys

import numpy as np
from Cython.Build import cythonize

# pyrefly: ignore [missing-source-for-stubs]
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
        name="cbemfmm.cbemfmm",
        sources=[
            "src/cbemfmm/cbemfmm.pyx",
            "src/cbemfmm/neighbor_ints_En.c",
            # "src/cbemfmm/neighbor_ints_Pn.c",
            "src/cbemfmm/potint.c",
            "src/cbemfmm/potint2.c",
        ],
        include_dirs=[
            np.get_include(),
            "src/cbemfmm",
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
            "cbemfmm",
        ],
    ),
)
