import struct

from mathutils import Matrix
from typing import NamedTuple
from .z_reader import ZReader


class BoneData(NamedTuple):
    transform: Matrix
    parent_id: int
    crc: int


class SkelZ(NamedTuple):
    crc: int
    bones: list[BoneData]


class SkelZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()
        self.bones: list[BoneData] = []

    def read_skel_z(self, data: bytes) -> SkelZ:
        self.load_data(data)

        self.bs.seek(0x10)
        class_crc = self.read_int32()
        skel_crc = self.read_int32()
        unk_crc = self.read_int32()
        self.read_uint16()
        self.read_uint16()
        bounds = struct.unpack("<4f", self.bs.read(16))

        bone_count = self.read_uint32()
        bones = []
        for _ in range(bone_count):
            self.bs.seek(164, 1)
            transform = self.read_matrix()
            self.read_int32()
            parent_id = self.read_int32()
            self.read_int32()
            self.read_int32()
            name_crc = self.read_int32()

            bones.append(BoneData(transform, parent_id, name_crc))

        material_count = self.read_uint32()
        material_crcs = [self.read_int32() for _ in range(material_count)]

        mesh_data_count = self.read_uint32()
        mesh_data_crcs = [self.read_int32() for _ in range(mesh_data_count)]

        # unk_count = self.read_uint32()

        # bone_crc_count_0 = self.read_uint32()
        # bone_crcs_0 = [self.read_int32() for _ in range(bone_crc_count_0)]

        # bone_crc_count_1 = self.read_uint32()
        # bone_crcs_1 = [self.read_int32() for _ in range(bone_crc_count_1)]

        return SkelZ(skel_crc, bones)
