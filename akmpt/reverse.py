import sys

from akmpt.base import ConnectedPointCollection
from akmpt.checkpoint import CheckPointGroup
from akmpt.kmp import Kmp


def reverse_kmp(kmp):
    """Reverses akmpt (EXPERIMENTAL, this only gives a starting place)"""
    if type(kmp) == str:
        kmp = Kmp(kmp)
    for routes in [kmp.routes, kmp.check_points, kmp.item_routes, kmp.cpu_routes]:
        for route in routes:
            reverse_route(route)
    reorder_key_checkpoints(kmp.check_points)
    rotate_group(kmp.respawns)
    rotate_group(kmp.start_positions)
    return kmp


def rotate_group(group):
    for item in group:
        item.rotation[1] = item.rotation[1] + 180 % 360


def reorder_key_checkpoints(checkpoints):
    key_points = {}  # create map to key checkpoints
    for group in checkpoints:
        for x in group:
            if x.key != 0xff:
                if x.key in key_points:
                    key_points[x.key].append(x)
                else:
                    key_points[x.key] = [x]

    key_sorted = sorted(list(key_points.keys()), reverse=True)
    start_line = key_points[key_sorted[-1]]
    assert start_line and start_line[0].key == 0
    for i in range(len(key_sorted)):
        for key_point in key_points[key_sorted[i]]:
            key_point.key = i + 1
    for item in start_line:
        item.key = 0


def reverse_route(route):
    route.points.reverse()
    if issubclass(type(route), ConnectedPointCollection):
        t = route.prev_groups
        route.prev_groups = route.next_groups
        route.next_groups = t
        if type(route) is CheckPointGroup:
            for check in route:
                t = check.next
                check.next = check.previous
                check.previous = t
                t = check.left_pole
                check.left_pole = check.right_pole
                check.right_pole = t
