from multiprocessing import Process

import matplotlib.pyplot as plt


def res_plot(resvec):
    plt.figure()
    plt.semilogy(resvec, "-o")
    plt.grid(True)
    plt.title("Relative residual of the iterative solution")
    plt.xlabel("Iteration number")
    plt.ylabel("Relative residual")
    plt.show()


def plot_residual(resvec):
    res_plot_p = Process(target=res_plot, args=(resvec,))
    res_plot_p.start()
    return res_plot_p
