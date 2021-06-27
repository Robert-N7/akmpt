#!/usr/bin/env python3

# Updates the version throughout files
import os
import re
import sys

from get_bit_width import get_bit_width


def get_last_update(version_file):
    if os.path.exists(version_file):
        with open(version_file) as f:
            return f.read()


def update_version(version):
    version_file = 'version'
    if version == get_last_update(version_file):
        print('Version already up to date')
        return 0
    version_files = ['../../setup.py', '../dist/install-ubu.txt', '../dist/install-win.txt', '../__main__.py',
                     'update_version.py', '../dist/make_installer.nsi',
                     '../load_config.py']
    # version_files = ['test.txt']
    rex = re.compile("(v(ersion)?\s*(\:|\=)?\s*(\"|\')?)\d+\.\d+\.\d+", re.IGNORECASE)
    replacement = '\g<1>' + version
    count = 0
    for x in version_files:
        if os.path.exists(x):
            with open(x) as file:
                fixed = rex.sub(replacement, file.read())
            with open(x, 'w') as file:
                file.write(fixed)
                count += 1
        else:
            print('WARN: Version file {} not found!'.format(x))
    with open(version_file, 'w') as f:
        f.write(version)
    return count


def update_bit_width(is_64_bit):
    filename = '../dist/make_installer.nsi'
    new_data = data = None
    str_width = '64' if is_64_bit else '32'
    with open(filename, 'r') as f:
        data = f.read()
        new_data, found = re.subn(r'^(InstallDir "\$PROGRAMFILES)\d*(\\abmatt")', '\g<1>' + str_width + '\g<2>', data,
                                  1, re.MULTILINE)
        if not found:
            print('Failed to replace bit width in installer')
    if new_data:
        with open(filename, 'w') as f:
            f.write(new_data)


def run_update_version(args, config=None):
    usage = 'update_version.py [version]'
    bit_width = version = None
    version = args.pop(0)
    if not re.match(r'\d+\.\d+\.\d+', version):
        print('Invalid version format {}'.format(version))
        sys.exit(1)
    bit_width = get_bit_width(sys.executable)
    is_64_bit = ['x86', 'x64'].index(bit_width)
    update_bit_width(is_64_bit)
    count = update_version(version)
    print('Updated version {} {} in {} files'.format(version, bit_width, count))


if __name__ == '__main__':
    run_update_version(sys.argv[1:])
