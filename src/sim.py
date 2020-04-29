#!/usr/bin/env python3
"""Simulation code"""
import sys
import time

import numpy as np

import plotter

T = 3000  # number of time steps


class Flock:
    """A flock of birds"""
    _w = 50   # wingspan
    _d = 50   # wash length
    _l = 30   # upwash width
    _dx = 3   # max lateral movment per step
    _dy = 3   # max longitudinal movment per step
    _e = 9    # min longitudinal seperation
    _t = 300  # threshold to swap positions

    def __init__(self, n):
        """Initialize Flock
        Args:
            n(uint): Number of birds in flock
        """
        self._n = n
        # initialize vars
        # lambda is amount of win over lap for optimal pos
        self._lambda = -0.1073 * Flock._w
        # downwash radius, max distance left / right following bird can be and
        # still be in downwash
        self._dr = Flock._w + self._lambda
        self._ur = self._dr + Flock._l
        # initialize birds and plot
        self._plot = plotter.Plot(self._w)
        # spread the birds out in some arbitrary way
        # x, y, energy
        self._birds = np.random.randn(n, 3) * n / 3 * self._w
        self._birds[:, 2] = 2000 + abs(np.random.randn(n)) * 1000
        self.plot()

    def plot(self):
        """update plot of flock"""
        self._plot.plot(self._birds)

    def step(self):
        """do a simulation timestep"""
        upwash = 0
        downwash = 0
        swarming = 0
        self._birds = self._birds[self._birds[:, 1].argsort()[::-1]]
        # front bird always flying in the open
        self._birds[0, 2] -= 3
        for bird in self._birds[1:, :]:
            # check if in proximity to another bird
            if not self._inwash(bird):
                # not close to another bird, find one to move towards
                self._swarm(bird)
                swarming += 1
                # take away 3 energy for flying in the open
                bird[2] -= 3
            else:
                # try and find a better view without doing more work
                self._adjust_view(bird)
                if self._downwash(bird):
                    downwash += 1
                    # take 5 energy to fly in downwash
                    bird[2] -= 5
                else:
                    upwash += 1
                    # take 1 energy to fly in upwash
                    bird[2] -= 1
                    drafter = self._upwash(bird)
                    if (drafter is not False
                            and drafter[2] < bird[2] - Flock._t):
                        drafter[2], bird[2] = bird[2], drafter[2]

        self.plot()
        # if converged, then sim over 
        #if upwash == self._n - 1:
        #    return True
        print(self._birds[:, 2].min())
        print(self._birds[:, 2].max())
        # if a bird is out of energy sim over
        if self._birds[:, 2].min() <= 0:
            return True
        print("upwash:   {}".format(upwash))
        print("downwash: {}".format(downwash))
        print("swarming: {}".format(swarming))
        return False

    def _swarm(self, bird):
        """move towards the closest bird to bird"""
        (x, y, _) = self._closest_bird(bird)
        if abs(x - bird[0]) <= self._ur:
            x = None
        self._move(bird, x, y)

    def _adjust_view(self, bird):
        """draft off of other birds to save energy"""
        try:
            pos = self._better_view(bird)
            # check don't move into downwash
            # or out of upwash
            # TODO no idea what logic should be here
            if self._downwash(bird):
                self._move(bird, *pos)
        except ValueError:
            print("This shouldn't be possible")

    def _infront(self, bird):
        """return all birds with >= y value, but not self"""
        return (b for b in self._birds if bird[1] <= b[1]
                and not (bird[1] == b[1] and bird[0] == b[0]))

    def _wash(self, bird):
        """return all birds bird is in the wash of"""
        return (b for b in self._infront(bird)
                if abs(b[1] - bird[1]) <= Flock._d)

    def _inwash(self, bird):
        """return if bird is in a wash"""
        for _ in (None for b in self._wash(bird)
                  if abs(b[0] - bird[0]) <= self._ur):
            return True
        return False

    def _downwash(self, bird):
        """return if bird is in a downwash"""
        for _ in (None for b in self._wash(bird)
                  if abs(b[0] - bird[0]) < self._dr - .01):
            return True
        return False

    def _upwash(self, bird):
        """return if bird is in a upwash"""
        for a in (b for b in self._wash(bird)
                  if self._dr < abs(b[0] - bird[0]) <= self._ur):
            return a
        return False

    def _closest_bird(self, bird):
        """find the closest bird, so can move towards it
        Args:
            bird(*(float,float)): reference to a bird(x,y) in self._birds
        Returns:
            (float, float): x,y of the bird closest to and infront of
            the given bird
        """
        return min(self._infront(bird),
                   key=lambda b: np.sqrt(np.sum(np.square(bird - b))))

    def _better_view(self, bird):
        """return the closest gap"""
        def views():
            """return x values that bird could see forward in"""
            birds = sorted((b[0] for b in self._infront(bird)))
            last = birds[0]
            yield last - self._dr
            for b in birds:
                if abs(b - last) >= 2 * self._dr:
                    yield last + self._dr
                    yield b - self._dr
                last = b
            yield last + self._dr
        return (min(views(),
                    key=lambda x: abs(x - bird[0])),
                bird[1])

    def _move(self, bird, x, y):
        """move the given bird towards x,y
        Args:
            bird(x,y): a reference to a bird in a flock
            x(float): an x value to move the bird towards
            y(float): a y value to move the bird towards
        """
        # TODO figure out how to move
        xdelta = 0
        ydelta = 0
        if x is not None:
            xdelta = x - bird[0]
            if abs(xdelta) > Flock._dx:
                if xdelta < 0:
                    xdelta = -Flock._dx
                else:
                    xdelta = Flock._dx
        if y is not None:
            ydelta = y - bird[1]
            if abs(ydelta) > Flock._dy:
                if ydelta < 0:
                    ydelta = -Flock._dy
                else:
                    ydelta = Flock._dy
            if abs(ydelta) > abs(xdelta):
                xdelta = 0
            else:
                ydelta = 0

        if abs(ydelta) >= abs(xdelta):
            xdelta = 0
        else:
            ydelta = 0
        # check move doesn't collid with other birds
        # if it does move bax dy
        for b in self._birds:
            if (abs(b[0] - (bird[0] + xdelta)) < Flock._w
               and abs(b[1] - (bird[1] + ydelta)) < Flock._e
               and bird[1] < b[1]):
                bird[1] -= ydelta
                return
        bird[0] += xdelta
        bird[1] += ydelta


def sim(n=20):
    """run simulation of a flock
    Args:
        n(uint): number of birds in flock
    """
    f = Flock(n)
    for i in range(T):
        if f.step():
            print(i)
            break
    print("Done!")
    time.sleep(5)


if __name__ == '__main__':
    cycles = 1
    if len(sys.argv) >= 3:
        cycles = int(sys.argv[2])
    for _ in range(cycles):
        if len(sys.argv) >= 2:
            sim(n=int(sys.argv[1]))
        else:
            sim()
