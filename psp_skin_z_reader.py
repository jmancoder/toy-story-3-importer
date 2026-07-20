import struct

from mathutils import Matrix
from typing import NamedTuple
from .z_reader import ZReader


class AttributePacket(NamedTuple):
    vertex_id: int
    weight: float


class PacketGroup(NamedTuple):
    unknown: int
    packets_0: list[AttributePacket]
    packets_1: list[AttributePacket]


class SkinZ(NamedTuple):
    flags: int
    crc: int
    skel_crc: int
    transform: Matrix
    mesh_crcs: list[int]
    attr_group_map: dict[int, list[PacketGroup]]


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

        bounds = struct.unpack("<4f", self.bs.read(16))
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

        # Read attribute packet groups
        group_count = self.read_uint32()
        attrib_group_map = {}
        for _ in range(group_count):
            group_crc = self.read_int32()
            packet_group_count = self.read_uint32()

            packet_groups = []
            for _ in range(packet_group_count):
                unk_1 = self.read_uint16()
                packet_count_0 = self.read_uint32()
                packets_0 = [
                    AttributePacket(*struct.unpack("<If", self.bs.read(8)))
                    for _ in range(packet_count_0)
                ]
                packet_count_1 = self.read_uint32()
                packets_1 = [
                    AttributePacket(*struct.unpack("<If", self.bs.read(8)))
                    for _ in range(packet_count_1)
                ]

                packet_groups.append(PacketGroup(unk_1, packets_0, packets_1))

            attrib_group_map[group_crc] = packet_groups

        return SkinZ(
            skin_flags,
            skin_crc,
            skel_crc,
            skin_transform,
            mesh_crcs,
            attrib_group_map,
        )
