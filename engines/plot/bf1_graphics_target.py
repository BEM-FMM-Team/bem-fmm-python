import numpy as np
import numpy.matlib
    
def bemf1_graphics_target(X = None,Y = None,Z = None,scale = None,transp = None): 
    #   Target plot
#   scale - parameter in mm
    
    #   Copyright SNM 2017-2022
    S = scipy.io.loadmat('sphere')
    n = len(S.P)
    for m in np.arange(1,len(X)+1).reshape(-1):
        p = patch('vertices',scale * S.P + 0.001 * np.matlib.repmat(np.array([X(m),Y(m),Z(m)]),n,1),'faces',S.t)
        p.FaceColor = np.array([1,0.2,0])
        np.array([255,249,81]) / 255
        p.EdgeColor = 'none'
        p.FaceAlpha = 1
    