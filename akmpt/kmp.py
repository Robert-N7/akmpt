import math
import os

from akmpt.cmon import pmap, mapa

from akmpt.lib.autofix import AutoFix
from akmpt.lib.packing.pack_kmp import PackKmp
from akmpt.lib.unpacking.unpack_kmp import UnpackKmp
from akmpt.respawn import Respawn
from akmpt.stage_info import StageInfo
from akmpt.start_position import StartPosition
from akmpt.lib.binfile import BinFile
from akmpt.lib.pack_interface import Packable
from akmpt.utils import distance


class Kmp(Packable):
    MAGIC = 'RKMD'

    @property
    def is_battle_mode(self):
        return len(self.end_positions) > 0

    def __init__(self, name, parent=None, read_file=True):
        self.object_map = None
        self.name = os.path.abspath(name)
        binfile = BinFile(self.name) if read_file else None
        if binfile:
            self.unpack(binfile)
        else:
            self.begin()

    def __create_obj_map(self):
        self.object_map = {}
        for x in self.game_objects:
            y = self.object_map.get(x.name)
            if not y:
                self.object_map[x.name] = [x]
            else:
                y.append(x)
        return self.object_map

    def get_height_at(self, x=0, z=0):
        return 10000

    def get_closest_cpu_pos(self, point):
        mins = [math.inf, math.inf]
        min_pos = [None, None]
        for r in self.cpu_routes:
            for pos in r:
                d = distance(pos.position, point)
                if d < mins[0]:
                    mins[1] = mins[0]
                    min_pos[1] = min_pos[0]
                    mins[0] = d
                    min_pos[0] = pos
                elif d < mins[1]:
                    mins[1] = d
                    min_pos[1] = pos
        return min_pos

    def get_start_checkpoint(self):
        for group in self.check_points:
            for x in group:
                if x.key == 0:
                    return x

    def begin(self):
        self.version = 0x9d8
        self.stage_info = [StageInfo()]
        self.areas = []
        self.cameras = []
        self.check_points = []
        self.cannons = []
        self.cpu_routes = []
        self.game_objects = []
        self.item_routes = []
        self.respawns = []
        self.start_positions = [StartPosition()]
        self.end_positions = []
        self.routes = []
        self.pan_cam = None
        self.movie_cam = None
        self.additional_values = [0] * 15

    def unpack(self, binfile):
        UnpackKmp(self, binfile)

    def pack(self, binfile):
        PackKmp(self, binfile)

    def __eq__(self, other):
        return self is other or \
               super().__eq__(other) and self.version == other.version and \
            self.stage_info == other.stage_info and \
            self.areas == other.areas and \
            self.cameras == other.cameras and \
            self.check_points == other.check_points and \
            self.cannons == other.cannons and \
            self.cpu_routes == other.cpu_routes and \
            self.game_objects == other.game_objects and \
            self.item_routes == other.item_routes and \
            self.respawns == other.respawns and \
            self.start_positions == other.start_positions and \
            self.end_positions == other.end_positions and \
            self.routes == other.routes and \
            self.pan_cam == other.pan_cam and \
            self.movie_cam == other.movie_cam

    def __getitem__(self, item):
        if type(item) is str:
            if not self.object_map:
                self.__create_obj_map()
            return self.object_map[item]
        else:
            return [x for x in self.game_objects if x.id == item]

    def check(self):
        if not self.respawns:
            AutoFix.warn('No respawns found! Adding generic...')
            self.respawns.append(Respawn([0, self.get_height_at(), 0]))

        # todo add cams
        if not self.pan_cam:
            AutoFix.warn('No opening pan camera!')
        if not self.movie_cam:
            AutoFix.warn('No movie cam!')

