from setuptools import setup, Extension
import numpy as np
import os
from pathlib import Path
import sys
from Cython.Build import cythonize

if sys.platform == "win32":
    compile_args = ["/O2", "/openmp"]
    link_args = ["/openmp"]
else:
    compile_args = ["-O3", "-fopenmp"]
    link_args = ["-fopenmp"]

ext = Extension(
    name="neighbor_ints_en_fmm",
    sources=[
        "neighbor_ints_Enpyx.pyx",
        "neighbor_ints_En.c",
    ],
    include_dirs=[ 
        np.get_include()
    ],
    extra_compile_args=compile_args,
    extra_link_args=link_args
)

setup(
    name="neighbor_ints_en_bemfmm",
    version="1.0",
    ext_modules=cythonize([ext]),

)