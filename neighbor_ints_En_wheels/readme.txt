To compile a wheel for your current system, make sure you have the modules "setuptools", "wheel", "Cython", and "numpy" pip installed in your environment. 
Navigate to this directory and run "Python -m build." The .whl will compile inside of the "dist" directory.
After pip installing the wheel, call it by importing "neighbor_ints_en_bemfmm", which contains the function "neighbor_ints_En" with signature
IE, IC = neighbor_ints_En(float nparray P,int nparray t,float nparray normal,float nparray center,int nparray neighbor,float nparray area, int gauss)