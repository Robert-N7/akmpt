import math

import numpy as np


def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)


def construct_linked_connections(connected_points):
    for route in connected_points:
        for i in range(1, len(route)):
            route[i - 1].next = [route[i]]
            route[i].prev = [route[i - 1]]
        route[-1].next = [r[0] for r in route.next_groups if r]
        route[0].prev = [r[-1] for r in route.prev_groups if r]


def get_y_rotation(origin, p2):
    """Get the y-rotation in degrees between two 3d points"""
    return math.atan2(p2[0] - origin[0], p2[2] - origin[2]) * 180 / math.pi


def is_ahead(left, right, p):
    return (right[0] - left[0]) * (right[1] - p[1]) - (right[1] - left[1]) * (right[0] - p[0]) > 0


def get_closest_p_on_line(point, lp1, lp2):
    p = np.array(lp1)
    q = np.array(lp2)
    r = np.array(point)
    v = q - p
    t = np.dot(v, p - r) / np.dot(v, v)
    return p - np.dot(t, v)
