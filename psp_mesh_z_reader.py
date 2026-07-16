import struct

from typing import NamedTuple
from mathutils import Matrix
from .z_reader import ZReader


class SubMesh(NamedTuple):
    transform: Matrix
    positions: list[tuple[float, float, float]]
    uvs: list[tuple[float, float]]
    unks_0: list[tuple[int, int, int, int]]
    unks_1: list[tuple[int, int, int, int]]
    triangles: list[tuple[int, int, int]]


class PSPMeshZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()
        self.transform: Matrix
        self.submeshes: list[SubMesh] = []
        self.uv_pool: list[tuple[float, float, float]] = []
        self.normal_pool: list[tuple[float, float, float]] = []
        self.unk_pool: list[int]

    def strips_to_triangles(self, strips: list[int]) -> list[tuple[int, int, int]]:
        indices = []
        flip = False
        i = 0
        while i < len(strips) - 2:
            a, b, c = strips[i], strips[i+1], strips[i+2]

            # Handle strip restart markers
            if a == -1:
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

    def load_data(self, data: bytes) -> None:
        super().load_data(data)

        # Partially read file header
        self.bs.seek(0x10)
        flags = self.read_uint32()
        hash = self.read_int32()
        self.read_int32()
        main_meshdata_hash = self.read_int32()
        unk_floats = struct.unpack("<4f", self.bs.read(16))
        self.transform = self.read_matrix()
        self.read_uint32()
        self.read_int32()
        self.read_uint16()
        meshdata_count = self.read_uint32()
        meshdata_hashes = [self.read_int32() for _ in range(meshdata_count)]
        self.read_uint32()
        # Potentially unreliable skip
        self.bs.seek(24, 1)

        uv_count = self.read_uint32()
        self.uvs = [
            struct.unpack("<2f", self.bs.read(8))
            for _ in range(uv_count)
        ]

        normal_count = self.read_uint32()
        self.normals = [
            struct.unpack("<3f", self.bs.read(12))
            for _ in range(normal_count)
        ]

        unk_attr_count = self.read_uint32()
        self.unk_pool = [
            self.read_int32()
            for _ in range(unk_attr_count)
        ]

        self.read_uint32()
        self.read_uint32()
        material_count = self.read_uint32()
        material_hashes = [self.read_int32() for _ in range(material_count)]
        # Another potentially unreliable skip
        self.bs.seek(48, 1)

        total_vertex_count = 0
        submesh_count = self.read_uint32()
        for i in range(submesh_count):
            # Read submesh header
            vertex_chunk_size = self.read_uint32()
            self.read_uint32()
            submesh_hashes = struct.unpack("<4i", self.bs.read(16))
            self.read_uint32()
            self.read_uint32()
            self.read_uint32()
            submesh_transform = self.read_matrix()

            submesh_end_off = self.bs.tell() + vertex_chunk_size
            vertex_count = (vertex_chunk_size - 20) // 18
            total_vertex_count += vertex_count
            print(f"Loaded mesh {i} with {vertex_count} vertices")
            self.bs.seek(20, 1)

            # Read vertices
            positions = []
            uvs = []
            unks_0 = []
            unks_1 = []
            strip_indices = []
            for i in range(vertex_count):
                unk_0 = struct.unpack("<4B", self.bs.read(4))
                uv = self.read_int16_vec(2)
                unk_1 = struct.unpack("<4B", self.bs.read(4))
                pos = self.read_int16_vec(3)

                if pos == -1:
                    strip_indices.append(-1)
                    continue
                
                unks_0.append(unk_0)
                uvs.append(uv)
                unks_1.append(unk_1)
                positions.append(pos)
                strip_indices.append(i)

            self.bs.seek(submesh_end_off)

            self.submeshes.append(SubMesh(
                submesh_transform,
                positions,
                uvs,
                unks_0,
                unks_1,
                self.strips_to_triangles(strip_indices),
            ))

        print("Total vertices:", total_vertex_count)

        unk_hash_count = self.read_uint32()
        unk_hashes = [self.read_int32() for _ in range(unk_hash_count)]
