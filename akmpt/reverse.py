import sys

from akmpt.base import ConnectedPointCollection
from akmpt.checkpoint import CheckPointGroup
from akmpt.kmp import Kmp
from akmpt.utils import construct_linked_connections, distance, get_y_rotation, get_closest_p_on_line


def reverse_kmp(kmp):
    """Reverses kmp (EXPERIMENTAL, this only gives a starting place)"""
    if type(kmp) == str:
        kmp = Kmp(kmp)
    for routes in [kmp.check_points, kmp.item_routes, kmp.cpu_routes]:
        for route in routes:
            reverse_route(route, kmp)
        first = routes[0]
        if len(first.next_groups):
            new_first = first.next_groups[0]
            routes.remove(new_first)
            routes.insert(0, new_first)
    reverse_cpu_offroad_routes(kmp.cpu_routes)
    reorder_key_checkpoints(kmp.check_points)
    construct_linked_connections(kmp.cpu_routes)
    reverse_respawns(kmp)
    reverse_start(kmp)
    return kmp


def reverse_cpu_offroad_routes(cpu_routes):
    for route in cpu_routes:
        if route[-1].settings[0] == 1:
            try:
                route[-1].settings[0] = 0
                route[-2].settings[0] = 0
                route[0].settings[0] = 1
                route[1].settings[0] = 2
            except IndexError:
                pass


def reverse_start(kmp):
    check_point = kmp.get_start_checkpoint()
    if not check_point:
        return
    left_pole = check_point.left_pole
    right_pole = check_point.right_pole

    for start in kmp.start_positions:
        mid_point = get_closest_p_on_line((start.position[0], start.position[2]), left_pole, right_pole)
        v = [start.position[0] - mid_point[0], start.position[2] - mid_point[1]]
        p = [mid_point[i] + v[i] * -1 for i in range(2)]
        start.position = [p[0], start.position[1], p[1]]
        p1, p2 = kmp.get_closest_cpu_pos(start.position)
        # Move the start position to the closest point on the line created by cpu points
        start.position = get_closest_p_on_line(start.position, p1.position, p2.position)
        towards = p2 if p2 in p1.next else p1
        start.rotation[1] = get_y_rotation(start.position, towards.position)


def reverse_respawns(kmp):
    for respawn in kmp.respawns:
        p1, p2 = kmp.get_closest_cpu_pos(respawn.position)
        if p1 in p2.next:
            move_toward = p1
        else:  # it might not even be a connected point?
            move_toward = p2
        d = 6000
        while True:
            d = move_on_line(respawn, move_toward, d)
            if d <= 0:
                break
            move_toward = move_toward.next[0]
        d = distance(respawn.position, move_toward.position)
        if d < 500:
            move_toward = move_toward.next[0]
        respawn.rotation[1] = get_y_rotation(respawn.position, move_toward.position)
        respawn.rotation[0] *= -1
        respawn.rotation[2] *= -1


def move_on_line(item, point, d):
    dist = distance(item.position, point.position)
    if dist > d:
        item.position = [(point.position[i] - item.position[i]) * d / dist + item.position[i] for i in range(3)]
        return 0
    else:  # move full amount
        item.position = [x for x in point.position]
        return d - dist


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


def reverse_route(route, kmp=None):
    route.points.reverse()
    if issubclass(type(route), ConnectedPointCollection):
        t = route.prev_groups
        route.prev_groups = route.next_groups
        route.next_groups = t
        if type(route) is CheckPointGroup:
            if route[-1].key == 0:
                start_line = route.points.pop(-1)
                if len(route.next_groups) == 1:
                    next = route.next_groups[0]
                    next.points.append(start_line)
                else:   # add a new checkpoint group in
                    ck_group = CheckPointGroup([start_line])
                    kmp.check_points.insert(0, ck_group)
                    ck_group.set_next_groups(route.next_groups)
                    route.set_next_groups([ck_group])
            for check in route:
                t = check.left_pole
                check.left_pole = check.right_pole
                check.right_pole = t
            route.rebuild_pointers()
    else:
        if len(route.points) > 1:
            p1 = route.points[-1]
            p0 = route.points[0]
            if p1.speed != 0 and p0.speed == 0:
                p0.speed = p1.speed
                p1.speed = 0
