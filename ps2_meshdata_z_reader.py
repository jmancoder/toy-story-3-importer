import struct

from mathutils import Vector
from .z_reader import ZReader


class PS2MeshDataZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()
        self.vertex_count = 0
        self.face_count = 0
        self.positions: list[Vector] = []
        self.unk_vert_values: list[int] = []
        self.triangles: list[tuple[int]] = []
        self.face_normals: list[tuple[int]] = []
        self.face_groups: list[tuple[int]] = []
        self.unk_face_values_0: list[int] = []
        self.unk_face_values_1: list[int] = []

    def load_data(self, data: bytes) -> None:
        super().load_data(data)
        
        # Read file header
        payload_size_0 = self.read_uint32()
        file_version = self.read_uint32()
        payload_size_1 = self.read_uint32()
        unk_flag_0 = self.read_uint32()
        file_hash = self.bs.read(12)
        unk_flag_1 = self.read_int32()
        if file_version == 4:
            print("Flags:", unk_flag_0, unk_flag_1)
        if file_version == 8:
            unk_flag_2 = self.read_int32()
            print("Flags:", unk_flag_0, unk_flag_1, unk_flag_2)

        # Read vertices
        self.vertex_count = self.read_uint32()
        for _ in range(self.vertex_count):
            self.positions.append(Vector(
                struct.unpack("<3f", self.bs.read(12))))
            self.read_int32()
        
        # Read secondary vertices
        vertex_count_1 = self.read_uint32()
        positions_1 = []
        for _ in range(vertex_count_1):
            positions_1.append(struct.unpack("<3f", self.bs.read(12)))
            self.unk_vert_values.append(self.read_int32())

        # Read faces
        self.face_count = self.read_uint32()
        for _ in range(self.face_count):
            self.triangles.append(struct.unpack("<3I", self.bs.read(12)))
            self.unk_face_values_0.append(self.read_int32())
            self.face_normals.append(struct.unpack("<3f", self.bs.read(12)))
            self.unk_face_values_1.append(self.read_uint32())
        
        # Read face groups
        face_group_count = self.read_uint32()
        for _ in range(face_group_count):
            self.face_groups.append(struct.unpack("<4I", self.bs.read(16)))
