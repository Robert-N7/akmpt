import os

from akmpt.lib.autofix import AutoFix
from akmpt.lib.binfile import BinFile


class Packer:
    def __init__(self, node, binfile):
        self.node = node
        self.binfile = binfile
        self.pack(node, binfile)

    def pack(self, node, binfile):
        raise NotImplementedError()


class Packable:
    overwrite = False

    def check(self):
        raise NotImplementedError()

    def unpack(self, binfile):
        raise NotImplementedError()

    def pack(self, binfile):
        raise NotImplementedError()

    def rename(self, name):
        self.name = name

    def save(self, filename=None, overwrite=None, check=True):
        if not filename:
            filename = self.name
        if overwrite is None:
            overwrite = self.overwrite
        if not overwrite and os.path.exists(filename):
            AutoFix.error('File {} already exists!'.format(filename), 1)
        else:
            if check:
                self.check()
            f = BinFile(filename, mode="w")
            self.pack(f)
            if f.commit_write():
                AutoFix.info("Wrote file '{}'".format(filename), 2)
                self.rename(filename)
                return True
        return False
