import sys

from akmpt.cmon.cmdline import run_cmds, ArgRunner
from akmpt.reverse import reverse_kmp


class ReverseRunner(ArgRunner):
    cmd = 'reverse'
    named_args = ('destination',)
    named_shortcuts = ('d',)
    flags = ('overwrite',)
    flag_shortcuts = ('o',)
    positional_args = ('filename',)
    default = 'destination'
    help_string = 'Reverses the checkpoints, item routes, cpu routes, and rotates respawns and start positions 180'

    def run(self):
        if not self.destination:
            self.destination = self.filename
        kmp = reverse_kmp(self.filename)
        return kmp.save(self.destination, self.overwrite)


def main():
    run_cmds(sys.argv[1:], 'Usage: reverse <kmp_file> [<destination>] [-o]')


if __name__ == '__main__':
    main()
