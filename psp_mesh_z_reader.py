import struct

from typing import NamedTuple
from mathutils import Matrix
from .z_reader import ZReader


class SubMesh(NamedTuple):
    transform: Matrix
    bone_crcs: tuple[int, int, int, int]
    positions: list[tuple[float, float, float]]
    weights: list[tuple[float, float, float, float]]
    uvs: list[tuple[float, float]]
    normals: list[tuple[float, float, float, float]]
    triangles: list[tuple[int, int, int]]


class MeshZ(NamedTuple):
    flags: int
    crc: int
    transform: Matrix
    submeshes: list[SubMesh]


class PSPMeshZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()

    def read_mesh_z(self, data: bytes) -> MeshZ:
        self.load_data(data)

        self.bs.seek(0x10)
        mesh_flags = self.read_uint32()
        mesh_crc = self.read_int32()
        self.read_int32()
        linked_mesh_data_crc = self.read_int32()

        bounds = struct.unpack("<4f", self.bs.read(16))
        mesh_transform = self.read_matrix()
        self.read_uint32()
        self.read_int32()
        self.read_uint16()
        mesh_data_count = self.read_uint32()
        mesh_data_crcs = [self.read_int32() for _ in range(mesh_data_count)]
        self.read_uint32()
        # Potentially unreliable skip
        self.bs.seek(24, 1)

        # Read unused attribute pools
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
            # Read submesh header
            chunk_size_padded = self.read_uint32()
            self.read_uint32()
            bone_crcs = struct.unpack("<4i", self.bs.read(16))
            self.read_uint32()
            self.read_uint32()
            self.read_uint32()
            submesh_transform = self.read_matrix()

            # Read vertex chunk header
            chunk_start = self.bs.tell()
            self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            chunk_size = self.read_uint16()
            self.read_uint16()

            positions = []
            uvs = []
            weights = []
            normals = []

            # Read vertices
            while self.bs.tell() < chunk_start + chunk_size:
                weight_raw = struct.unpack("<4B", self.bs.read(4))
                if weight_raw == (255, 255, 255, 255):
                    # Skip initial 0xFF bytes
                    continue
                weight = tuple(val / 128 for val in weight_raw)

                x, y = struct.unpack("<2h", self.bs.read(4))
                uv = ((x / 2048) - 8.0, (y / 2048) - 8.0)

                x, y, z, w = struct.unpack("<4b", self.bs.read(4))
                normal = (x / 128, y / 128, z / 128)

                x, y, z = struct.unpack("<3h", self.bs.read(6))
                pos = (x / 32767, y / 32767, z / 32767)

                weights.append(weight)
                uvs.append(uv)
                normals.append(normal)
                positions.append(pos)

            # Read vertex chunk footer
            self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            unk_flag = self.read_uint16()
            self.read_uint16()
            vertex_count = self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            self.read_uint16()
            self.bs.seek(chunk_start + chunk_size_padded)

            # Generate triangles from strip-ordered positions
            triangles = []
            flip = True
            for i in range(len(positions) - 2):
                a, b, c = positions[i:i+3]
                if a == b or b == c or a == c:
                    # Skip degenerate triangles formed by repeated vertices
                    flip = not flip
                    continue

                if not flip:
                    triangles.append((i, i + 1, i + 2))
                else:
                    triangles.append((i, i + 2, i + 1))
                flip = not flip

            submeshes.append(SubMesh(
                submesh_transform,
                bone_crcs,
                positions,
                weights,
                uvs,
                normals,
                triangles,
            ))

        unk_crc_count = self.read_uint32()
        unk_crcs = [self.read_int32() for _ in range(unk_crc_count)]

        return MeshZ(
            mesh_flags,
            mesh_crc,
            mesh_transform,
            submeshes,
        )
