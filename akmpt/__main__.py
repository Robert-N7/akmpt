import sys

from akmpt.kmp import Kmp

from akmpt.cmon.cmdline import run_cmds, ArgRunner
from akmpt.reverse import reverse_kmp, reverse_route


def create_slice(mystring):
    return slice(*map(lambda x: int(x.strip()) if x.strip() else None, mystring.split(':')))


class GenericRunner(ArgRunner):
    named_args = ('destination',)
    named_shortcuts = ('d',)
    flags = ('overwrite',)
    flag_shortcuts = ('o',)
    positional_args = ('filename',)
    default = 'destination'

    def run(self):
        if not self.destination:
            self.destination = self.filename
        self.kmp = Kmp(self.filename)

    def save(self):
        return self.kmp.save(self.destination, self.overwrite)


class ReverseRunner(GenericRunner):
    cmd = 'reverse'
    named_args = ('destination', 'route')
    help_string = 'Reverses the checkpoints, item routes, cpu routes, and rotates respawns and start positions 180\n' \
                  '\t\tSpecify route=<route_index> to reverse a route instead'

    def run(self):
        super().run()
        if self.route:
            reverse_route(self.kmp.routes[self.route])
        else:
            reverse_kmp(self.kmp)
        return self.save()


class RotateRunner(GenericRunner):
    cmd = 'rotate'
    named_args = ('destination', 'group', 'item', 'rotation', 'direction')
    help_string = 'rotates the kmp <group> [<item>] by rotation (default 180)'
    rotation_default = 180
    group_default = 'game_objects'
    direction_default = 'y'

    def rotate_group(self, group):
        if hasattr(group, '__iter__'):
            for item in group:
                item.rotation[self.direction_index] = (item.rotation[self.direction_index] + self.rotation) % 360
        else:
            group.rotation[self.direction_index] = (group.rotation[self.direction_index] + self.rotation) % 360

    def run(self):
        super().run()
        kmp = self.kmp
        self.direction_index = 'xyz'.index(self.direction)
        group = getattr(kmp, self.group)
        if self.item:
            try:
                self.slice = create_slice(self.item)
            except ValueError:
                self.slice = self.item
            if group is kmp.game_objects:
                group = kmp
            for x in group[self.slice]:
                self.rotate_group(x)
        else:
            for x in group:
                self.rotate_group(x)
        return self.save()


def main():
    run_cmds(sys.argv[1:], 'Usage: (reverse|rotate) <kmp_file> [<destination>] [-o]',
             (ReverseRunner, RotateRunner))


if __name__ == '__main__':
    main()
