from setuptools import setup, Extension
import numpy as np
import os
from pathlib import Path
import sys
from Cython.Build import cythonize


print("SETUP.PY DIR =", os.path.abspath(os.path.dirname(__file__)))
here = Path(__file__).resolve().parent

if sys.platform == "win32":
    compile_args = ["/O2", "/openmp"]
    link_args = ["/openmp"]
else:
    compile_args = ["-O3", "-fopenmp"]
    link_args = ["-fopenmp"]

ext = Extension(
    name="neighbor_ints_en_fmm",
    sources=[
        here/"neighbor_ints_Enpyx.pyx",
        here/"neighbor_ints_En.c",
    ],
    include_dirs=[
        str(here),    
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