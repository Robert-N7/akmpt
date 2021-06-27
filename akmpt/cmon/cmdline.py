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
    default = None          # for random arg
    positional_args = None  # Must be at beginning in order (required)
    on_unknown = ON_UNKNOWN_ERR

    def __init__(self):
        if self.flags:
            for i in range(len(self.flags)):
                setattr(self, self.flags[i], False)
        if self.named_args:
            for i in range(len(self.named_args)):
                try:
                    val = getattr(self, self.named_args[i] + '_default')
                except AttributeError:
                    val = None
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
                j += 1
                continue
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
    if args:
        s = ''
        for a in args:
            if a not in f_map:
                raise ValueError(f'No such cmd {a}')
            runner = f_map[a]
            s += a
            for x in runner.positional_args:
                s += ' <' + x + '>'
            if len(runner.named_args) or len(runner.flags):
                s += ' ['
                for i in range(len(runner.named_args)):
                    try:
                        named = '-' + runner.named_shortcuts[i]
                    except IndexError:
                        named = '--' + runner.named_args[i]
                    s += named + '=<' + runner.named_args[i] + '> '
                for x in runner.flags:
                    s += '--' + x + ' '
                s = s[:-1] + ']'
            s += '\n'
            s += '  ' + a + ' ' * (9 - (len(a) % 8)) + runner.help_string + '\n'
    else:
        s = usage + '\n'
        for x in f_map:
            s += '  ' + x + ' ' * (9 - (len(x) % 8)) + f_map[x].help_string + '\n'
        s += '  -h,--help [<cmd>]    Display help message' + '\n'
    print(s)


def run_cmds(args, usage=f'usage: <cmd> <args>', arg_runners=None, default=None, additional_help=''):
    """
    Runs commands using the function map
    :param args: all arguments
    :param usage: usage string
    :param arg_runners: list of ArgRunner classes, default is all subclasses
    :param default: the default command to run if none specified
    :param additional_help: help string to add at the bottom of generic help.
    :return: results from functions
    """
    if arg_runners is None:
        arg_runners = ArgRunner.__subclasses__()
    if not args:
        if default is None:
            default = '-h'
        args.append(default)

    m = mapa('cmd', arg_runners)
    results = []
    while args is not None and len(args):
        arg = args.pop(0)
        if arg in ('-h', '--help'):
            print_help(args, m, usage)
            if not args:
                print(additional_help)
            return results
        else:
            k = m[arg]()
            args = k.parse_args(args)
            results.append(k.run())
    return results
