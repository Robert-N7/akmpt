from akmpt.cmon import mapa


class ArgParseError(Exception):
    pass


class ArgRunner:
    ON_UNKNOWN_ERR = 0
    ON_UNKNOWN_STOP = 1
    ON_UNKNOWN_IGNORE = 2

    cmd = None
    help_string = '(Unknown)'
    flags = None            # --flag
    flag_shortcuts = None   # -f
    named_args = None       # destination=<file>
    named_shortcuts = None  # -d <file>
    named_defaults = None
    default = None          # for random arg
    positional_args = None  # Must be at beginning in order (required)
    on_unknown = ON_UNKNOWN_ERR

    def __init__(self):
        if self.flags:
            for i in range(len(self.flags)):
                setattr(self, self.flags[i], False)
        if self.named_args:
            for i in range(len(self.named_args)):
                val = self.named_defaults[i] if self.named_defaults else None
                setattr(self, self.named_args[i], val)
        setattr(self, self.default, None)

    def run(self):
        raise NotImplementedError()

    def _on_unknown_arg(self, arg):
        if self.on_unknown == self.ON_UNKNOWN_ERR:
            raise ArgParseError(f'Unknown arg {arg}!')
        elif self.on_unknown == self.ON_UNKNOWN_STOP:
            return True

    def parse_args(self, args):
        if self.positional_args and len(args) < len(self.positional_args):
            raise ArgParseError(f'{self.cmd} requires {len(self.positional_args)} args!')
        default_set = False
        j = 0
        while j < len(args):
            a = args[j]
            if self.positional_args and j < len(self.positional_args):
                setattr(self, self.positional_args[j], a)
            flag = a.startswith('-')
            a = a.lstrip('-')
            i = a.find('=')
            if i > -1:
                attr = a[:i]
                if attr not in self.named_args:
                    if self._on_unknown_arg(a):
                        return args[j:]
                setattr(self, attr, a[i + 1:])
            elif flag:
                if a not in self.flags:
                    try:
                        k = self.flag_shortcuts.index(a)
                        setattr(self, self.flags[k], True)
                    except ValueError:
                        try:
                            k = self.named_shortcuts.index(a)
                            j += 1
                            setattr(self, self.named_args[k], args[j])
                        except ValueError:
                            if self._on_unknown_arg(a):
                                return args[j:]
                else:
                    setattr(self, a, True)
            elif not self.default or default_set:
                if self._on_unknown_arg(a):
                    return args[j:]
            else:
                setattr(self, self.default, a)
                default_set = True
            j += 1


def print_help(args, f_map, usage):
    s = usage + '\n'
    if args:
        for a in args:
            if a not in f_map:
                raise ValueError(f'No such cmd {a}')
            s += '\t' + a + '\t' + f_map[a].help_string + '\n'
    else:
        for x in f_map:
            s += '\t' + x + '\t' + f_map[x].help_string + '\n'
        s += '\t-h,--help [<cmd>]\t' + 'Display help message ' + '\n'
    print(s)


def run_cmds(args, usage=f'usage: <cmd> <args>', arg_runners=None):
    """
    Runs commands using the function map
    :param args: all arguments
    :param usage: usage string
    :param arg_runners: list of ArgRunner classes, default is all subclasses
    :return: results from functions
    """
    if arg_runners is None:
        arg_runners = ArgRunner.__subclasses__()
    m = mapa('cmd', arg_runners)
    results = []
    while args is not None and len(args):
        arg = args.pop(0)
        if arg in ('-h', '--help'):
            print_help(args, m, usage)
        else:
            k = m[arg]()
            args = k.parse_args(args)
            results.append(k.run())
    return results
