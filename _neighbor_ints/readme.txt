# notes
cython neighbor_ints_Enpyx.pyx # to generate the cython file during dev so the user does not need Cython

In [1]: import neighbor_ints
In [2]: neighbor_ints.neighbor_ints_En()


To compile a wheel for your current system, make sure you have the modules "setuptools", "wheel", "Cython", and "numpy" pip installed in your environment (you can use the requirements.txt).
Navigate to this directory and run "Python -m build." The .whl will compile inside of the "dist" directory.
After pip installing the wheel, call it by importing "neighbor_ints_en_bemfmm", which contains the function "neighbor_ints_En" with signature
IE, IC = neighbor_ints_En(float nparray P,int nparray t,float nparray normal,float nparray center,int nparray neighbor,float nparray area, int gauss)
