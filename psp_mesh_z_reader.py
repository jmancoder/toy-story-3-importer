import struct

from typing import NamedTuple
from mathutils import Matrix, Vector
from .z_reader import ZReader


class SubMesh(NamedTuple):
    transform: Matrix
    bone_name_crcs: tuple[int, int, int, int]
    positions: list[tuple[float, float, float]]
    unk_attr: list[tuple[int, int, int, int]]
    uvs: list[tuple[float, float]]
    binormals: list[tuple[float, float, float, float]]
    triangles: list[tuple[int, int, int]]


class MeshZ(NamedTuple):
    flags: int
    crc: int
    transform: Matrix
    uv_pool: list[tuple[float, float, float]]
    normal_pool: list[tuple[float, float, float]]
    unk_attr_pool: list[int]
    submeshes: list[SubMesh]


class PSPMeshZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()

    def read_position(self) -> tuple[float, float]:
        x, y = struct.unpack("<2H", self.bs.read(4))
        return (x / 0x7FFF, y / 0x7FFF)

    def strips_to_triangles(self, strips: list[int]) -> list[tuple[int, int, int]]:
        indices = []
        flip = False
        i = 0
        while i < len(strips) - 2:
            a, b, c = strips[i], strips[i+1], strips[i+2]

            # Skip degenerate triangles
            if a == b or a == c or b == c:
                i += 1
                flip = False
                continue

            if flip:
                indices.append((a, b, c))
            else:
                indices.append((a, c, b))

            flip = not flip
            i += 1

        return indices

    def read_mesh_z(self, data: bytes) -> MeshZ:
        self.load_data(data)

        self.bs.seek(0x10)
        mesh_flags = self.read_uint32()
        mesh_crc = self.read_int32()
        self.read_int32()
        linked_mesh_data_crc = self.read_int32()

        unk_vec = struct.unpack("<4f", self.bs.read(16))
        mesh_transform = self.read_matrix()
        self.read_uint32()
        self.read_int32()
        self.read_uint16()
        mesh_data_count = self.read_uint32()
        mesh_data_crcs = [self.read_int32() for _ in range(mesh_data_count)]
        self.read_uint32()
        # Potentially unreliable skip
        self.bs.seek(24, 1)

        # Read attribute pools
        uv_count = self.read_uint32()
        uv_pool = [
            struct.unpack("<2f", self.bs.read(8))
            for _ in range(uv_count)
        ]

        normal_count = self.read_uint32()
        normal_pool = [
            struct.unpack("<3f", self.bs.read(12))
            for _ in range(normal_count)
        ]

        unk_attr_count = self.read_uint32()
        unk_attr_pool = [
            self.read_int32()
            for _ in range(unk_attr_count)
        ]

        self.read_uint32()
        self.read_uint32()
        material_count = self.read_uint32()
        material_crcs = [self.read_int32() for _ in range(material_count)]
        # Another potentially unreliable skip
        self.bs.seek(48, 1)

        # Read submeshes
        submesh_count = self.read_uint32()
        submeshes = []
        for i in range(submesh_count):
            vertex_chunk_size = self.read_uint32()
            self.read_uint32()
            bone_name_crcs = struct.unpack("<4i", self.bs.read(16))
            self.read_uint32()
            self.read_uint32()
            self.read_uint32()
            submesh_transform = self.read_matrix()

            submesh_end_off = self.bs.tell() + vertex_chunk_size
            self.bs.seek(12, 1)

            positions = []
            uvs = []
            unk_attrs = []
            binormals = []
            strip_indices = []

            # Read vertices
            prev_position = (-1 / 32767) * 3
            i = 0
            while self.bs.tell() <= submesh_end_off - 18:
                unk_attr = struct.unpack("<4b", self.bs.read(4))
                if unk_attr == (-1, -1, -1, -1):
                    # Skip initial 0xFF bytes
                    continue
                if unk_attr == (34, -61, 0, 18):
                    # Stop before consistent unknown data at end of vertex buffer
                    break

                x, y = struct.unpack("<2h", self.bs.read(4))
                uv = ((x / 2048) - 8.0, (y / 2048) - 8.0)

                x, y, z, w = struct.unpack("<4B", self.bs.read(4))
                binormal = (x / 255, y / 255, z / 255, w / 255)

                x, y, z = struct.unpack("<3h", self.bs.read(6))
                position = (x / 32767, y / 32767, z / 32767)

                unk_attrs.append(unk_attr)
                uvs.append(uv)
                binormals.append(binormal)
                positions.append(position)

                if position == prev_position:
                    # Store degenerate triangle when vertex position is repeated
                    strip_indices.append(i - 1)
                else:
                    strip_indices.append(i)

                prev_position = position
                i += 1

            self.bs.seek(submesh_end_off)

            submeshes.append(SubMesh(
                submesh_transform,
                bone_name_crcs,
                positions,
                unk_attrs,
                uvs,
                binormals,
                self.strips_to_triangles(strip_indices),
            ))

        unk_crc_count = self.read_uint32()
        unk_crcs = [self.read_int32() for _ in range(unk_crc_count)]

        return MeshZ(
            mesh_flags,
            mesh_crc,
            mesh_transform,
            uv_pool,
            normal_pool,
            unk_attr_pool,
            submeshes,
        )
