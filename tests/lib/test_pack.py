import os

from tests.base import Base
from akmpt.kmp import Kmp
from tests.lib.file_compare import file_compare


class TestPack(Base):
    def test_beginner_pack_eq(self):
        self._test_pack_eq('beginner.kmp')

    def test_casino_pack_eq(self):
        self._test_pack_eq('casino.kmp')
