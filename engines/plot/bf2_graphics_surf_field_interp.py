import numpy as np
import matplotlib.pyplot as plt
    
def bemf2_graphics_surf_field_interp(P = None,t = None,FQ = None,Indicator = None,objectnumber = None): 
    #   Surface field graphics:  plot a field quantity FQ at the surface of a
#   brain compartment with the number "tissuenumber". Interpolates over
#   triangles
    
    #   Copyright SNM 2017-2021
    
    ##  Interpolation for nodes
    t0 = t(Indicator == objectnumber,:)
    Pobs,tobs = fixmesh(P,t0)
    TR = triangulation(tobs,Pobs)
    V = vertexAttachments(TR)
    N = Pobs.shape[1-1]
    tempnodes = np.zeros((N,1))
    for m in np.arange(1,N+1).reshape(-1):
        tempnodes[m] = mean(FQ(V[m]))
    
    ##   Graphics - interpolation plot
    Ptemp = np.transpose(Pobs)
    ttemp = np.transpose(tobs)
    X = np.reshape(Ptemp(1,ttemp(np.arange(1,3+1),:)), tuple(np.array([3,ttemp.shape[2-1]])), order="F")
    Y = np.reshape(Ptemp(2,ttemp(np.arange(1,3+1),:)), tuple(np.array([3,ttemp.shape[2-1]])), order="F")
    Z = np.reshape(Ptemp(3,ttemp(np.arange(1,3+1),:)), tuple(np.array([3,ttemp.shape[2-1]])), order="F")
    ##   Interpolate field for vertexes - global
    temp = np.transpose(tempnodes)
    C = temp(ttemp(np.arange(1,3+1),:))
    ##  Plot
    patch(X,Y,Z,C,'FaceAlpha',1.0,'EdgeColor','none','FaceLighting','flat')
    colorbar
    plt.axis('equal')
    plt.axis('tight')
    plt.xlabel('x, m')
    plt.ylabel('y, m')
    plt.zlabel('z, m')
    set(gcf,'Color','White')
    return
    