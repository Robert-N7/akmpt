from akmpt import reverse
from akmpt.utils import is_ahead, get_y_rotation
from tests.base import Base


class TestReverse(Base):
    def test_reversed(self):
        original = self._get_kmp('beginner.kmp')
        reversed = reverse.reverse_kmp(original)
        start_line = reversed.check_points[0][0]
        self.assertTrue(start_line.key == 0)
        self.assertTrue(start_line.previous is None)
        self.assertIsNotNone(start_line.next)
        start_cpu = reversed.cpu_routes[0][0]
        self.assertTrue(is_ahead(start_line.left_pole, start_line.right_pole, (start_cpu.position[0],
                                                                               start_cpu.position[2])))
        start_pos = reversed.start_positions[0]
        alignment = get_y_rotation(start_pos.position, start_cpu.position)
        self.assertTrue(alignment == start_pos.rotation[1])
