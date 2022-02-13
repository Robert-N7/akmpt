class Base:
    FMT = None
    BYTE_LEN = None
    MAGIC = None

    @staticmethod
    def init_3(args):
        return [list(x) if x else [0, 0, 0] for x in args]

    def __eq__(self, other):
        return other is not None and type(other) is type(self)


class PointCollection(Base):

    def __init__(self, points=None):
        self.points = points if points is not None else []

    def __len__(self):
        return len(self.points)

    def __getitem__(self, item):
        return self.points[item]

    def __setitem__(self, key, value):
        self.points[key] = value

    def __iter__(self):
        return iter(self.points)

    def __next__(self):
        return next(self.points)


class ConnectedPointCollection(PointCollection):
    FMT = '16B'
    BYTE_LEN = 0x10

    def __init__(self, points=None, settings=None):
        super().__init__(points)
        self.next_groups = []
        self.prev_groups = []
        self.settings = [0, 0] if not settings else settings

    def __eq__(self, o):
        return self is o or super().__eq__(o) \
               and self.points == o.points and self.settings == o.settings

    def add_next_group(self, group):
        self.next_groups.append(group)
        group.prev_groups.append(self)
    
    def set_next_groups(self, groups):
        for x in self.next_groups:
            try:
                x.prev_groups.remove(self)
            except ValueError:
                pass
        self.next_groups = []
        for x in groups:
            self.add_next_group(x)
    
    def remove_next_group(self, group):
        try:
            self.next_groups.remove(group)
            group.prev_groups.remove(self)
        except ValueError:
            pass

    def add_prev_group(self, group):
        self.prev_groups.append(group)
        group.next_groups.append(self)

    def remove_prev_group(self, group):
        try:
            self.prev_groups.remove(group)
            group.next_groups.remove(self)
        except ValueError:
            pass
    
    def set_prev_groups(self, groups):
        for x in self.prev_groups:
            try:
                x.next_groups.remove(self)
            except ValueError:
                pass
        self.prev_groups = []
        for x in groups:
            self.add_prev_group(x)