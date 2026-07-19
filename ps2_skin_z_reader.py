import struct

from typing import NamedTuple
from mathutils import Matrix
from .z_reader import ZReader


class SkinZ(NamedTuple):
    flags: int
    crc: int
    skel_crc: int
    transform: Matrix
    mesh_crcs: list[int]


class PS2SkinZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()

    def read_skin_z(self, data: bytes) -> SkinZ:
        self.load_data(data)

        self.bs.seek(0x10)
        skin_flags = self.read_uint32()
        skin_crc = self.read_int32()
        self.read_int32()
        skel_crc = self.read_int32()

        bounds = struct.unpack("<4f", self.bs.read(16))
        transform = self.read_matrix()
        self.read_uint32()
        self.read_uint32()
        self.read_uint16()

        mesh_count = self.read_uint32()
        mesh_crcs = [self.read_int32() for _ in range(mesh_count)]

        return SkinZ(
            skin_flags,
            skin_crc,
            skel_crc,
            transform,
            mesh_crcs,
        )
