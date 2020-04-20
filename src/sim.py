#!/usr/bin/env python3
"""Simulation code"""
import numpy as np

import plotter

T = 4000  # number of time steps

class Flock:
    """A flock of birds"""
    def __init__(self, n):
        """Initialize Flock
        Args:
            n(uint): Number of birds in flock
        """
        # initialize vars
        # TODO comment what they are
        self._w = 50
        self._lambda = -0.1073 * self._w
        self._d = 50
        self._l = 30
        self._dx = 3
        self._dy = 3
        self._epsilon = 9
        self._downwash_radius = (self._w / 2) + self._lambda
        self._upwash_radius = self._downwash_radius + self._l
        # initialize birds and plot
        self._plot = plotter.Plot(self._w)
        # spread the birds out in some arbitrary way
        self._birds = np.random.randn(n, 2) * n / 3 * self._w
        self.plot()

    def plot(self):
        """update plot of flock"""
        self._plot.plot(self._birds)

    def step(self):
        """do a simulation timestep"""
        self._birds = self._birds[self._birds[:, 1].argsort()[::-1]]
        for bird in self._birds:
            # check if in proximity to another bird
            if not self._inwash(bird):
                # not close to another bird, find one to move towards
                try:
                    self._swarm(bird)
                except ValueError:
                    continue
            else:
                self._get_upwash(bird)
        self.plot()

    def _swarm(self, bird):
        """move towards the closest bird to bird"""
        closest_bird = self._closest_bird(bird)
        # if x diff is large then move in x
        if abs(closest_bird[0] - bird[0]) > self._upwash_radius:
            ydelta = None
            # if y diff is big move diagonally so converge faster
            if abs(closest_bird[1] - bird[1]) > 3 * self._d:
                ydelta = closest_bird[1]
            self._move(bird, closest_bird[0], ydelta)
        else:
            self._move(bird, None, closest_bird[1])

    def _get_upwash(self, bird):
        """draft off of other birds to save energy"""
        # find drafting position to move into
        pos = self._closest_pos(bird)
        # check if x value is close
        if abs(pos[0] - bird[0]) > self._dx:
            y = None
            # if y diff is big move diagonally so converge faster
            if abs(pos[1] - bird[1]) > 3 * self._d:
                y = pos[1]
            self._move(bird, pos[0], y)
        else:
            self._move(bird, None, pos[1])

# REVIEW FROM HERE

    def _infront(self, bird):
        """generator of all birds in front of bird
        Args:
            bird(*(float, float)): reference to a bird(x,y) in self._birds
        Returns:
            Generator(float,float): generator that yields x,y coords of birds
            in front of the given bird
        """
        return (b for b in self._birds if bird[1] <= b[1]
                and not (bird[1] == b[1] and bird[0] == b[0]))

    def _inwash(self, bird):
        """Check if bird is in another birds wash
        Args:
            bird(*(float, float)): reference to abird(x,y) in self._birds
        Returns:
            bool: if bird is in the wash of any other birds
        """
        # find birds that are in front of bird, +/- upwash_radius
        # and within _d in front of bird
        for _ in (b for b in self._infront(bird) if
                  abs(b[0] - bird[0]) <= self._upwash_radius
                  and b[1] <= self._d + bird[1]):
            return True
        return False

    def _closest_bird(self, bird):
        """find the closest bird, so can move towards it
        Args:
            bird(*(float,float)): reference to a bird(x,y) in self._birds
        Returns:
            (float, float): x,y of the bird closest to and infront of
            the given bird
        """
        def dist(a, b):
            """define dist between two points"""
            return np.sqrt(np.sum(np.square(a - b)))

        # find bird that is min dist and infront of bird
        r = min(self._infront(bird), key=lambda b: dist(b, bird))
        # give coord of behind bird
        return (r[0], r[1] - self._epsilon)

    def _closest_pos(self, bird):
        """find the closest pos for bird to move towards
        Args:
            bird(*(float, float)): reference to a bird(x,y) in self._birds
        Returns:
            (float, float): the closest x,y position that bird can move in to
            and be in a gap
        """
        # shift is how far +/- x following bird should be to get updraft
        shift = self._w + self._lambda
        # optimal positions for a bird are on the edge of a gap
        # gap is a x range of >= 2*self._wingspan +2 * self._lambda
        gap_width = 2 * shift
        # with no other birds in front
        # sort all birds in front (by x)
        infront = sorted(self._infront(bird), key=lambda x: x[0])

        def positions():
            # yield all possible optimal positions for bird
            last = infront[0]
            # iter through all birds looking for gaps
            for b in infront[1:]:
                if abs(b[0] - last[0]) >= gap_width:
                    # yield left side of gap
                    yield (last[0] + shift, last[1] - self._epsilon)
                    # yield right side of gap
                    yield (b[0] - shift, b[1] - self._epsilon)
                last = b
            # yield far right gap
            yield (last[0] + shift, last[1] - self._epsilon)
        # return the position closest to bird
        return min(positions(), key=lambda p: abs(p[0] - bird[0]))

    def _move(self, bird, x, y):
        """move the given bird towards x,y
        Args:
            bird(x,y): a reference to a bird in a flock
            x(float): an x value to move the bird towards
            y(float): a y value to move the bird towards
        """
        xdelta = 0
        ydelta = 0
        if x is not None:
            xdelta = x - bird[0]
            if abs(xdelta) > self._dx:
                if xdelta < 0:
                    xdelta = -self._dx
                else:
                    xdelta = self._dx
        elif y is not None:
            ydelta = y - bird[1]
            if abs(ydelta) > self._dy:
                if ydelta < 0:
                    ydelta = -self._dy
                else:
                    ydelta = self._dy
        # check move doesn't collid with other birds
        for b in self._infront(bird):
            if abs(b[0] - (bird[0] + xdelta)) < self._w + 2 * self._lambda \
               and abs(b[1] - (bird[1] + ydelta)) < self._epsilon:
                bird[1] -= ydelta
                return
        bird[0] += xdelta
        bird[1] += ydelta


def sim(n=25):
    """run simulation of a flock
    Args:
        n(uint): number of birds in flock
    """
    f = Flock(n)
    for _ in range(T):
        f.step()


if __name__ == '__main__':
    sim()
