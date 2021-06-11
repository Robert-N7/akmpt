import os
import unittest

from akmpt.kmp import Kmp
from tests.lib.file_compare import file_compare


class Base(unittest.TestCase):
    def tearDown(self):
        try:
            os.remove(self.tmp)
        except (AttributeError, FileNotFoundError):
            pass

    def _test_pack_eq(self, fname):
        if type(fname) is str:
            original = Kmp(self._get_test_fname(fname))
        else:
            original = fname
        name = original.name
        original.save(self._get_tmp('kmp'), overwrite=True)
        if not file_compare(name, original.name):
            new = Kmp(original.name)
            self.assertTrue(original == new)
            raise ValueError(f'{name} packed not equal!')

    def _get_test_fname(self, filename):
        return os.path.join(os.path.dirname(__file__), 'fixtures', filename)

    def _get_kmp(self, filename):
        if not filename.endswith('.kmp'):
            filename += '.kmp'
        return Kmp(self._get_test_fname(filename))
    
    def _get_tmp(self, ext='.kmp'):
        if ext[0] != '.':
            ext = '.' + ext
        self.tmp = self._get_test_fname('tmp' + ext)
        return self.tmp
