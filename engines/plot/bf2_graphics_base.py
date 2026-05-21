import numpy as np
    
def bemf2_graphics_base(P = None,t = None,c = None): 
    #   Surface plot
    
    #   Copyright SNM 2017-2020
    
    p = patch('vertices',P,'faces',t)
    p.FaceColor = c.FaceColor
    p.EdgeColor = c.EdgeColor
    p.FaceAlpha = c.FaceAlpha
    daspect(np.array([1,1,1]))
    NumberOfTrianglesInShell = t.shape[1-1]
    edges = meshconnee(t)
    temp = P(edges(:,1),:) - P(edges(:,2),:)
    AvgEdgeLengthInShell = mean(np.sqrt(np.dot(temp,temp,2)))
    return
    