import numpy as np
    
def fgmres(A = None,b = None,tol = None,varargin = None): 
    # Flexible GMRES method
#   [x,iter] = fgmres(A, b, tol, varargin)
    
    # Tries to solve a linear system Ax=b via the flexible GMRES
    
    # A should be given as a function handle @(x)A(x), which computes the
# Matrix-Vector product A*x.
    
    # A and b can be passed as regular double arrays
    
    # varargin may contain a sequence of tuning parameters of the form
# 'parameter1_name', parameter1_value, 'parameter2_name', parameter2_value
# and so on. Available parameters and [default values] are the following.
#   'relaxation' [0]: Inexact Krylov relaxation power. The accuracy for
#                       Krylov vectors is set as tol/(|r|/|b|)^relaxation,
#                       where r is the current residual
#   'max_iters' [2]: Number of outer iterations
#   'restart' [20]: Number of inner iterations
#   'x0' [all-zeros vector]: Initial guess
#   'verb' [2]:  Verbosity. 0 - Silent, 1 - outer iteration info, 2 - inner
#                iteration info, 3 - iterations + return all solutions in td{2}
#   'tol_exit' [tol]:  Stopping tolerance: exit if |r|/|b|<tol_exit
#   'P' []: Preconditioning procedure in the same form as A, i.e. @(x)P(x)
    
    
    # Returns the solution x iteration numbers iter and residuals resids
    
    
    # Development: Sergey Dolgov ( sergey.v.dolgov@gmail.com ),
# Max Planck Institute for Mathematics in the Sciences, Leipzig.
    
    #TT-Toolbox 2.2, 2009-2012
    
    #This is TT Toolbox, written by Ivan Oseledets et al.
#Institute of Numerical Mathematics, Moscow, Russia
#webpage: http://spring.inm.ras.ru/osel
    
    #For all questions, bugs and suggestions please mail
#ivan.oseledets@gmail.com
#---------------------------
    
    # Inexact Krylov relaxation power. The accuracy for Krylov vectors is set
# as tol/(|r|/|b|)^relaxation, where r is the current residual
    relaxation = 0
    # Number of outer iterations
    max_iters = 1
    # Number of inner iterations
    restart = 100
    # Initial guess
    x = []
    # Verbosity
    verb = 2
    # Stopping tolerance
    tol_exit = tol
    # Prec
    P = []
    for i in np.arange(1,len(varargin) - 1+2,2).reshape(-1):
        if 'relaxation' == varargin[i].lower():
            relaxation = varargin[i + 1]
        else:
            if 'max_iters' == varargin[i].lower():
                max_iters = varargin[i + 1]
            else:
                if 'restart' == varargin[i].lower():
                    restart = varargin[i + 1]
                else:
                    if 'x0' == varargin[i].lower():
                        x = varargin[i + 1]
                    else:
                        if 'verb' == varargin[i].lower():
                            verb = varargin[i + 1]
                        else:
                            if 'tol_exit' == varargin[i].lower():
                                tol_exit = varargin[i + 1]
                            else:
                                if 'p' == varargin[i].lower():
                                    P = varargin[i + 1]
                                else:
                                    raise Exception('Unknown tuning parameter "%s"',varargin[i])
    
    # If we are given a single matrix, just use exact MV
    if (True):
        A = lambda x = None: (A * x)
    
    if (not len(P)==0 ) and (True):
        P = lambda x = None: (P * x)
    
    n = b.shape[1-1]
    if (restart > n):
        restart = n
    
    # Norm of the RHS
    beta0 = norm(b)
    if (beta0 == 0):
        x = np.zeros((n,1))
        iter = 0
        resids = 0
        return x,iter,resids
    
    # Check for the initial guess
    if (len(x)==0):
        x = np.zeros((n,1))
    
    t_gmres_start = tic
    # # Hessinberg matrix
# H = zeros(restart+1, restart);
# Householder data
    W = np.zeros((restart + 1,1))
    R = np.zeros((restart,restart))
    J = np.zeros((2,restart))
    # Krylov subspace
    V = cell(restart,1)
    # Preconditioned subspace
    if (not len(P)==0 ):
        Z = cell(restart,1)
    
    if (nargout > 2):
        resids = np.zeros((restart,max_iters))
    
    for it in np.arange(1,max_iters+1).reshape(-1):
        # Krylov tolerance
        tol_kryl = tol
        # Compute the initial residual
        if (it > 1) or (norm(x) > 0):
            Ax = A(x)
            u = b - Ax
        else:
            u = b
        beta = norm(u)
        # Prepare the first Householder vector
        if (u(1) < 0):
            beta = - beta
        u[1] = u(1) + beta
        u = u / norm(u)
        # The first Hh entry
        W[1] = - beta
        V[0] = u
        for j in np.arange(1,restart+1).reshape(-1):
            # Construct the last vector from the HH storage
#  Form P1*P2*P3...Pj*ej.
#  v = Pj*ej = ej - 2*u*u'*ej
            v = - 2 * conj(u(j)) * u
            v[j] = v(j) + 1
            #  v = P1*P2*...Pjm1*(Pj*ej)
            for i in np.arange((j - 1),1+- 1,- 1).reshape(-1):
                v = v - 2 * V[i] * (np.transpose(V[i]) * v)
            #  Explicitly normalize v to reduce the effects of round-off.
            v = v / norm(v)
            if (len(P)==0):
                w = A(v)
            else:
                # Keep the PrecVec separately
                Z[j] = P(v)
                w = A(Z[j])
            # Orthogonalize the Krylov vector
#  Form Pj*Pj-1*...P1*Av.
            for i in np.arange(1,j+1).reshape(-1):
                w = w - 2 * V[i] * (np.transpose(V[i]) * w)
            # Update the rotators
#  Determine Pj+1.
            if (j != len(w)):
                #  Construct u for Householder reflector Pj+1.
                u = np.array([[np.zeros((j,1))],[w(np.arange(j + 1,end()+1))]])
                alpha = norm(u)
                if (alpha != 0):
                    if (w(j + 1) < 0):
                        alpha = - alpha
                    u[j + 1] = u(j + 1) + alpha
                    u = u / norm(u)
                    V[j + 1] = u
                    #  Apply Pj+1 to v.
#  v = v - 2*u*(u'*v);
                    w[np.arange[j + 2,end()+1]] = 0
                    w[j + 1] = - alpha
            #  Apply Given's rotations to the newly formed v.
            for colJ in np.arange(1,j - 1+1).reshape(-1):
                tmpv = w(colJ)
                w[colJ] = conj(J(1,colJ)) * w(colJ) + conj(J(2,colJ)) * w(colJ + 1)
                w[colJ + 1] = - J(2,colJ) * tmpv + J(1,colJ) * w(colJ + 1)
            #  Compute Given's rotation Jm.
            if (j != len(w)):
                rho = norm(w(np.arange(j,j + 1+1)))
                J[:,j] = w(np.arange(j,j + 1+1)) / rho
                W[j + 1] = np.multiply(- J(2,j),W(j))
                W[j] = np.multiply(conj(J(1,j)),W(j))
                w[j] = rho
                w[j + 1] = 0
            R[:,j] = w(np.arange(1,restart+1))
            # Local and global residuals
            err = np.abs(W(j + 1)) / np.abs(beta)
            resid = np.abs(W(j + 1)) / beta0
            # Relax the Krylov tolerance
            tol_kryl = tol / (err ** relaxation)
            # report the residual
            if (nargout > 2):
                resids[j,it] = resid
            if (verb > 1):
                print('iter=%d, resid=%3.3e, locerr=%3.3e, time=%g\n' % (j,resid,err,toc(t_gmres_start)))
            if (resid < tol_exit):
                break
        # Correction
        y = np.linalg.solve(R(np.arange(1,j+1),np.arange(1,j+1)),W(np.arange(1,j+1)))
        if (len(P)==0):
            dx = - 2 * y(j) * V[j] * conj(V[j](j))
            dx[j] = dx(j) + y(j)
            for i in np.arange(j - 1,1+- 1,- 1).reshape(-1):
                dx[i] = dx(i) + y(i)
                dx = dx - 2 * V[i] * (np.transpose(V[i]) * dx)
        else:
            dx = np.zeros((n,1))
            for i in np.arange(j,1+- 1,- 1).reshape(-1):
                dx = dx + y(i) * Z[i]
        x = x + dx
        if (resid < tol_exit):
            break
    
    # Output
    if (nargout > 1):
        iter = np.array([it,j])
    
    if (nargout > 2):
        resids = resids(:,np.arange(1,it+1))
        resids[np.arange[j + 1,restart+1],it] = resid
    
    return x,iter,resids
    
    return x,iter,resids