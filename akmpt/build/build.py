#!/usr/bin/env python3
import os
import platform
import shutil
import subprocess
import sys
import time

from check_imports import ImportChecker
from get_bit_width import get_bit_width
from update_version import run_update_version


def which(program):
    def is_exe(exe_file):
        return os.path.isfile(exe_file) and os.access(exe_file, os.X_OK)

    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, program)
        if is_exe(exe_file):
            return exe_file
        exe_file += '.exe'
        if is_exe(exe_file):
            return exe_file


def run_sub_process(args, cwd, program=None):
    if program is None:
        li = [sys.executable]
    else:
        li = [program]
    li.extend(args)
    return subprocess.Popen(li, cwd=cwd)


def build_distribution(version):
    interpreter = sys.executable
    os.chdir('../dist')
    # read configuration
    bit_width = get_bit_width(interpreter)
    name = 'main'
    build_type = 'dir'
    # build
    clean([name, ], [name + '.exe', name, ])
    my_platform = platform.system().lower()
    if 'windows' in my_platform:
        makensis = which('makensis')
        if not makensis:
            raise FileNotFoundError('makensis')
        win_zip = which('7z')
        if not win_zip:
            raise FileNotFoundError('7z')
    else:
        makensis = win_zip = None
    out_file, is_dir = build(name, build_type, interpreter, my_platform)
    if not out_file:
        sys.exit(1)
    dist_dir = 'akmpt_' + my_platform + '-' + platform.release() + '_' \
               + bit_width + '-' + version
    # clean
    clean([dist_dir], (dist_dir + '.zip', dist_dir + '.tar.gz', 'dist_dir'))
    # dist
    if not make_distribution(dist_dir, my_platform, out_file, is_dir, makensis, win_zip):
        sys.exit(1)


def main(args):
    # update version/bit_width
    start = time.time()
    if (len(args)):
        version = args[0]
    else:
        print('Version required!')
        sys.exit(1)
    run_update_version([version])
    abspath = os.path.abspath(__file__)
    x = ImportChecker(os.path.dirname(os.path.dirname(abspath)))
    x.check_imports()
    build_distribution(version)
    print(f'Finished in {round(time.time() - start, 2)} secs.')


def tar(path):
    return not os.system('tar czvf ' + path + '.tar.gz ' + path)


def zip(path, win_zip):
    return not os.system(f'"{win_zip}" a -tzip {path}.zip {path}')


def make_distribution(dir, platform, binary_path, binary_path_is_dir, make_nsis, win_zip):
    os.mkdir(dir)
    print(f'Making distribution in {dir}')
    shutil.copy('../../LICENSE', dir)
    shutil.copy('../../README.md', dir)
    # etc = dir + '../etc/akmpt'
    # copy_from = '../../etc/akmpt'
    # for file in os.listdir(copy_from):
    #     path = os.path.join(copy_from, file)
    #     if not os.path.isdir(path):
    #         shutil.copy(path, etc)
    dest_dir = os.path.join(dir, 'bin')
    bin_dir, base_name = os.path.split(binary_path)
    exe = os.path.join(dest_dir, 'akmpt')
    is_exe = False
    if 'exe' in base_name:
        is_exe = True
        base_name, ext = os.path.splitext(base_name)
    if binary_path_is_dir:
        shutil.copytree(bin_dir, dest_dir)
        if is_exe:
            shutil.move(os.path.join(dest_dir, base_name + '.exe'), exe + '.exe')
        else:
            shutil.move(os.path.join(dest_dir, base_name), exe)
    else:
        os.mkdir(dest_dir)
        shutil.copy(binary_path, exe)
    # platform specific files
    if platform == 'windows':
        shutil.copy('./install-win.txt', dir)
        shutil.copy('./make_installer.nsi', dir)
        os.chdir(dir)
        if os.system(f'"{make_nsis}" make_installer.nsi'):
            return False
        os.remove('./make_installer.nsi')
        os.chdir('..')
        if not zip(dir, win_zip):
            return False
    else:
        install_file = './install-ubu.txt'
        update_os(install_file, platform)
        shutil.copy(install_file, os.path.join(dir, 'install.txt'))
        if not tar(dir):
            os.chdir('..')
            return False
        os.chdir('..')
    return True


def copytree(folder, dest, replace_existing=False):
    if not os.path.exists(dest):
        os.mkdir(dest)
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            copytree(path, os.path.join(dest, file), replace_existing)
        else:
            file_dest = os.path.join(dest, file)
            if not os.path.exists(file_dest):
                shutil.copy2(path, file_dest)
            elif replace_existing:
                os.remove(file_dest)
                shutil.copy2(path, file_dest)


def update_os(file, platform):
    with open(file) as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if line.startswith('OS:'):
            new_lines.append('OS: ' + platform + '\n')
        else:
            new_lines.append(line)
    with open(file, 'w') as f:
        f.write(''.join(new_lines))


def clean(folders, files):
    for folder in folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            shutil.rmtree(folder)
    for x in files:
        if os.path.exists(x) and os.path.isfile(x):
            os.remove(x)


def build(name, build_type, interpreter, platform):
    output = None
    os.chdir('..')
    for x in os.listdir():
        if x.endswith('.pyc'):
            os.remove(x)
    if 'dir' in build_type:
        output_type = '--onedir'
    elif 'file' in build_type:
        output_type = '--onefile'
    else:
        output_type = '--onedir' if platform == 'windows' else 'onefile'
    is_dir = True if 'onedir' in output_type else False
    params = '-y __main__.py --name ' + name + ' ' + output_type
    print('Current dir is {}'.format(os.getcwd()))
    # if platform == 'windows':
    params += ' -i ./dist/icon.ico'
    result = os.system(interpreter + ' -m PyInstaller ' + params)
    os.chdir('dist')
    if not result:
        output = name if not is_dir else name + '/' + name
        if not os.path.exists(output) or os.path.isdir(output):
            output += '.exe'
            if not os.path.exists(output):
                print('Unable to find PyInstaller output file!')
                sys.exit(1)
        result = os.system(os.path.join(os.getcwd(),
                                        output) + ' reverse ../../tests/fixtures/beginner.kmp '
                                                  '../../tests/fixtures/tmp.kmp -o')
        if not result:
            return output, is_dir
    return None, is_dir


if __name__ == '__main__':
    main(sys.argv[1:])
    print('done')
