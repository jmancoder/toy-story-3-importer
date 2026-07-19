import struct

from mathutils import Matrix
from typing import NamedTuple
from .z_reader import ZReader


class PointGroup(NamedTuple):
    unk_0: int
    unk_1: int
    unk_2: int
    points_0: list[tuple[int, float]]
    points_1: list[tuple[int, float]]


class SkinZ(NamedTuple):
    flags: int
    crc: int
    skel_crc: int
    transform: Matrix
    mesh_crcs: list[int]
    point_group_map: dict[int, PointGroup]


class PSPSkinZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()

    def read_skin_z(self, data: bytes) -> SkinZ:
        super().load_data(data)

        self.bs.seek(0x10)
        skin_flags = self.read_uint32()
        skin_crc = self.read_int32()
        unk_crc = self.read_int32()
        skel_crc = self.read_int32()

        unk_vec = struct.unpack("<4f", self.bs.read(16))
        skin_transform = self.read_matrix()
        self.read_uint32()
        self.read_uint32()
        self.read_uint16()
        mesh_crc_count = self.read_uint32()
        mesh_crcs = [
            self.read_int32()
            for _ in range(mesh_crc_count)
        ]
        self.read_uint32()

        # Read entry groups
        group_count = self.read_uint32()
        point_group_map = {}
        for _ in range(group_count):
            group_crc = self.read_int32()
            unk_0 = self.read_int16()
            unk_1 = self.read_int16()
            unk_2 = self.read_int16()

            entry_count_0 = self.read_uint32()
            points_0 = [
                struct.unpack("<If", self.bs.read(8))
                for _ in range(entry_count_0)
            ]

            entry_count_1 = self.read_uint32()
            points_1 = [
                struct.unpack("<If", self.bs.read(8))
                for _ in range(entry_count_1)
            ]

            point_group_map[group_crc] = PointGroup(
                unk_0,
                unk_1,
                unk_2,
                points_0,
                points_1,
            )

        return SkinZ(
            skin_flags,
            skin_crc,
            skel_crc,
            skin_transform,
            mesh_crcs,
            point_group_map,
        )
