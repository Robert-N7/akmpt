from akmpt import reverse
from tests.base import Base


class TestReverse(Base):
    def test_reverse_eq(self):
        original = self._get_kmp('beginner.kmp')
        reversed = reverse.reverse_kmp(original)
        normal = reverse.reverse_kmp(reversed)
        normal.save(self._get_tmp(), overwrite=True)
        self.assertEqual(original, normal)
