from typing import List

class IsoFrameInfo:
    def __init__(self):
        self.time_sec: float = 0.0
        self.level: int = 0
        self.ver_count: int = 0
        self.tri_count: int = 0
        self.byte_size: int = 0
        self.vert_start_offset: int = 0
        self.acc_byte_size: int = 0
    def serialize(self):
        return {
        'time_sec': self.time_sec,
        'level': self.level,
        'ver_count': self.ver_count,
        'tri_count': self.tri_count,
        'byte_size': self.byte_size,
        'vert_start_offset': self.vert_start_offset,
        'acc_byte_size': self.acc_byte_size
        }


class IsoVertex:
    def __init__(self):
        self.XYZ = [0.0] * 3
    def serialize(self):
        return {
            "XYZ": self.XYZ
        }

class IsoTriangle:
    def __init__(self):
        self.XYZW = [0] * 4
    def serialize(self):
        return {
            "XYZW": self.XYZW
        }


class IsoVertAndTri:
    def __init__(self):
        self.vertices: List[IsoVertex] = []
        self.triangles: List[IsoTriangle] = []
        self.time_sec: float = 0.0
        # self.next_sec: float = 0.0
        self.cur_frame: int = 0
        # self.total_frame: int = 0
        self.dt: float = 0
    def serialize(self):
        return {
            "vertices": [v.serialize() for v in self.vertices],
            "triangles": [t.serialize() for t in self.triangles],
            "time_sec": self.time_sec,
            # "next_sec": self.next_sec,
            "cur_frame": self.cur_frame,
            # "total_frame": self.total_frame,
            "dt": self.dt
        }