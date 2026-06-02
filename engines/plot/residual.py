from multiprocessing import Process

import matplotlib.pyplot as plt


def plot_residual(resvec):
    def res_plot():
        plt.figure()
        plt.semilogy(resvec, "-o")
        plt.grid(True)
        plt.title("Relative residual of the iterative solution")
        plt.xlabel("Iteration number")
        plt.ylabel("Relative residual")
        plt.show()

    res_plot_p = Process(target=res_plot)
    res_plot_p.start()
