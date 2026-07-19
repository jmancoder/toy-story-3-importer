import struct

from typing import NamedTuple
from mathutils import Matrix
from .z_reader import ZReader


class MeshZ(NamedTuple):
    flags: int
    crc: int
    transform: Matrix
    mesh_data_crc: int


class PS2MeshZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()

    def read_mesh_z(self, data: bytes) -> MeshZ:
        self.load_data(data)

        self.bs.seek(0x10)
        mesh_flags = self.read_uint32()
        mesh_crc = self.read_int32()
        self.read_int32()
        self.read_int32()

        bounds = struct.unpack("<4f", self.bs.read(16))
        transform = self.read_matrix()
        self.read_uint32()
        self.read_uint32()
        self.read_uint16()
        self.read_uint32()
        mesh_data_crc = self.read_int32()

        return MeshZ(
            mesh_flags,
            mesh_crc,
            transform,
            mesh_data_crc,
        )
