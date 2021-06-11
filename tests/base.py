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
