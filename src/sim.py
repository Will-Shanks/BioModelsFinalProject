#!/usr/bin/env python3
"""Simulation code"""
import numpy as np

import plotter

WINGSPAN = 50
LAMBDA = -0.1073 * WINGSPAN
# Downwash is WINGSPAN + 2LAMBDA wide
# lateral seperation should be >= WINGPSAN + LAMBDA, with = being optimal
D = 50  # A Birds wash only extends D behind it
L = 30  # A Birds upwash extend L laterally out from its downwash
DX = 3
DY = 3
EPSILON = 9
T = 2000
N = 25
UPWASH_RADIUS=(WINGSPAN/2) + LAMBDA + L
DOWNWASH_RADIUS = (WINGSPAN/2) + LAMBDA

def gaps(b):
    yield (b[0]-UPWASH_RADIUS, b[0]-DOWNWASH_RADIUS)
    last = b[0]
    for i in b:
        if i-last >= UPWASH_RADIUS:
            yield (last+DOWNWASH_RADIUS,i-DOWNWASH_RADIUS)
            last = i
    yield (b[len(b)-1]+DOWNWASH_RADIUS, b[len(b)-1]+UPWASH_RADIUS)

def x_dist(bird, gap):
    return min(abs(bird-gap[0]), abs(bird-gap[1]))

def dist(a, b):
    return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5

def sim():
    def in_front(bird):
        # returns generator of all birds that bird is in the wash of
        return (b for b in birds if
                b[0] - UPWASH_RADIUS <= bird[0] <= b[0] + UPWASH_RADIUS
                and bird[1]+EPSILON < b[1] <= bird[1] + D)

    def rule1(bird):
        # false if need to apply rule 1
        return len(list(in_front(bird))) > 0

    def closest_gap(bird):
        b = list((x[0] for x in in_front(bird)))
        b.sort()
        closest = None
        if b is None:
            return bird
        for gap in gaps(b):
            if closest is None or x_dist(bird[0], gap) < x_dist(bird[0], closest):
                closest = gap
        return closest

    def closest_bird(bird):
        closest = None
        for b in birds:
            if b is bird or b[1] < bird[1]+EPSILON:
                continue
            if closest is None or dist(bird,b) < dist(closest, bird):
                closest = b
        return closest


    # initialize birds and plot
    p = plotter.Plot(WINGSPAN)
    birds = np.random.randn(N, 2) * N / 3 * WINGSPAN
    p.plot(birds)
    #TODO implement collision avoidance
    for _ in range(T):
        for bird in birds:
            if not rule1(bird):
                move_to = closest_bird(bird)
                if move_to is None:
                    continue
                # move +-DX or +DY (not -DY) towards nearest bird
                elif abs(bird[0]-move_to[0]) < move_to[1]-bird[1]:
                    bird[1] += min(DY, move_to[1]-bird[1])
                elif move_to[0] > bird[0]:
                    bird[0] += min(move_to[0]-bird[0], DX)
                else:
                    bird[0] -= min(move_to[0], DX)

            else:
                gap = closest_gap(bird)
                if gap[0] > bird[0]:
                     bird[0] += min(DX, gap[0]-bird[0])
                elif gap[1] < bird[0]:
                    bird[0] -= min(DX, bird[0]-gap[1])
                else:
                    if bird[0]-gap[0] < gap[1]-bird[0]:
                        bird[0] -= min(DX, bird[0]-gap[0])
                    else:
                        bird[0] += min(DX, gap[1] - bird[0])
        p.plot(birds)


if __name__ == '__main__':
    sim()
