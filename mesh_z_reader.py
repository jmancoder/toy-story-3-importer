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
    crc: int
    transform: Matrix
    submeshes: list[SubMesh]


class MeshZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()

    def read_triangle_strips(self,
            positions: list[tuple[float, float, float]]
            ) -> list[tuple[int, int, int]]:
        triangles = []
        flip = True
        for i in range(len(positions) - 2):
            a, b, c = positions[i:i+3]
            if a == b or b == c or a == c:
                # Skip degenerate triangles formed by repeated positions
                flip = not flip
                continue

            if not flip:
                triangles.append((i, i + 1, i + 2))
            else:
                triangles.append((i, i + 2, i + 1))
            flip = not flip

        return triangles

    def read_mesh_z(self, data: bytes) -> MeshZ:
        self.load_data(data)

        self.bs.seek(0x10)
        class_crc = self.read_int32()
        mesh_crc = self.read_int32()
        link_crc = self.read_int32()
        main_mesh_data_crc = self.read_int32()

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
        for _ in range(submesh_count):
            # Read submesh header
            chunk_size_padded = self.read_uint32()
            self.read_uint32()
            bone_crcs = struct.unpack("<4i", self.bs.read(16))
            self.read_uint32()
            self.read_uint32()
            self.read_uint32()
            submesh_transform = self.read_matrix()

            # Read vertex chunk header
            chunk_header_off = self.bs.tell()
            self.read_uint24()
            self.read_uint8()
            self.read_uint24()
            self.read_uint8()
            rel_footer_off = self.read_uint24()
            self.read_uint8()

            # Read vertex chunk footer first
            self.bs.seek(chunk_header_off + rel_footer_off)
            self.read_uint24()
            self.read_uint8()
            self.read_uint24()
            self.read_uint8()
            chunk_header_size = self.read_uint24()
            self.read_uint8()
            vertex_count = self.read_uint16()
            prim_type = self.read_uint8()
            self.read_uint8()
            self.read_uint24()
            self.read_uint8()
            self.read_uint24()
            self.read_uint8()

            # Read vertices
            self.bs.seek(chunk_header_off + chunk_header_size)

            positions = []
            uvs = []
            weights = []
            normals = []
            for _ in range(vertex_count):
                a, b, c, d = struct.unpack("<4B", self.bs.read(4))
                weight = (a / 128, b / 128, c / 128, d / 128)

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

            # Skip to next vertex chunk
            self.bs.seek(chunk_header_off + chunk_size_padded)

            # Generate triangles according to the primitive type
            if prim_type < 3:
                triangles = []
            elif prim_type == 3:
                triangles = [(i, i+2, i+1) for i in range(0, vertex_count, 3)]
            elif prim_type == 4:
                triangles = self.read_triangle_strips(positions)
            elif prim_type == 5:
                triangles = []
                print("Warning: Triangle fan primitives are unimplemented.")
            elif prim_type == 6:
                triangles = []
                print("Warning: Sprite primitives are unimplemented.")
            else:
                triangles = []
                print("Warning: Unknown primitive type", prim_type)

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
            mesh_crc,
            mesh_transform,
            submeshes,
        )
