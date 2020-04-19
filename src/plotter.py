#!/usr/bin/env python3
"""Plotting functions"""

from matplotlib import pyplot as plt


class Plot:
    """Plot represents a plot"""
    def __init__(self, wingspan):
        self.wingspan = wingspan
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

    def plot(self, points):
        """Plots the given points
        Args:
            points (np.ndarray(2,)): xy coordinates of each point
        """
        self.ax.clear()
        self.ax.scatter(points[:, 0], points[:, 1], color="k", s=150)
        self.ax.errorbar(points[:, 0], points[:, 1], xerr=self.wingspan / 2,
                         linestyle="None", color="k")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


if __name__ == '__main__':
    import numpy as np
    import time
    p = Plot(1)
    for i in range(10):
        p.plot(np.array([[1, 1 + i / 10], [2, 2], [3, 3], [4 + i / 10, 4]]))
    time.sleep(2)
