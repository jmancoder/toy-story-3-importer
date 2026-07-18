import struct

from typing import NamedTuple
from mathutils import Vector
from .z_reader import ZReader


class MeshDataZ(NamedTuple):
    flags: int
    crc: int
    positions_0: list[Vector]
    unk_vert_attrs_0: list[int]
    positions_1: list[Vector]
    unk_vert_attrs_1: list[int]
    triangles: list[tuple[int]]
    unk_face_attrs_0: list[int]
    face_normals: list[tuple[int]]
    unk_face_attrs_1: list[int]
    face_groups: list[tuple[int]]


class PS2MeshDataZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()

    def read_mesh_data_z(self, data: bytes) -> MeshDataZ:
        self.load_data(data)

        self.bs.seek(0x10)
        mesh_data_flags = self.read_uint32()
        mesh_data_crc = self.read_int32()
        self.read_int32()
        self.read_int32()
        self.read_int32()
        self.read_int32()

        # Read vertices
        positions_0 = []
        unk_vert_attrs_0 = []
        vertex_count_0 = self.read_uint32()
        for _ in range(vertex_count_0):
            positions_0.append(Vector(
                struct.unpack("<3f", self.bs.read(12))))
            unk_vert_attrs_0.append(self.read_int32())

        # Read secondary vertices
        positions_1 = []
        unk_vert_attrs_1 = []
        vertex_count_1 = self.read_uint32()
        for _ in range(vertex_count_1):
            positions_1.append(struct.unpack("<3f", self.bs.read(12)))
            unk_vert_attrs_1.append(self.read_int32())

        # Read faces
        triangles = []
        unk_face_attrs_0 = []
        face_normals = []
        unk_face_attrs_1 = []
        face_count = self.read_uint32()
        for _ in range(face_count):
            triangles.append(struct.unpack("<3I", self.bs.read(12)))
            unk_face_attrs_0.append(self.read_int32())
            face_normals.append(struct.unpack("<3f", self.bs.read(12)))
            unk_face_attrs_1.append(self.read_uint32())

        # Read face groups
        face_groups = []
        face_group_count = self.read_uint32()
        for _ in range(face_group_count):
            face_groups.append(struct.unpack("<4I", self.bs.read(16)))

        return MeshDataZ(
            mesh_data_flags,
            mesh_data_crc,
            positions_0,
            unk_vert_attrs_0,
            positions_1,
            unk_vert_attrs_1,
            triangles,
            unk_face_attrs_0,
            face_normals,
            unk_face_attrs_1,
            face_groups,
        )
