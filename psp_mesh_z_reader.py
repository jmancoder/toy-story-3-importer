import struct

from typing import NamedTuple
from mathutils import Vector, Matrix
from .z_reader import ZReader


class SubMesh(NamedTuple):
    transform: Matrix
    positions: list[Vector]
    triangles: list[tuple[int]]


class PSPMeshZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()
        self.transform: Matrix
        self.submeshes: list[SubMesh] = []
        self.uvs: list[tuple[int]] = []
        self.normals: list[tuple[int]] = []
        self.colors: list[tuple[int]]

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

        color_count = self.read_uint32()
        self.colors = [
            struct.unpack("<4B", self.bs.read(4))
            for _ in range(color_count)
        ]

        self.read_uint32()
        self.read_uint32()
        unk_count = self.read_uint32()
        unk_vals = [self.read_int32() for _ in range(unk_count)]
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
            vertex_count = (vertex_chunk_size - 14) // 18
            total_vertex_count += vertex_count
            print(f"Loaded mesh {i} with {vertex_count} vertices")
            self.bs.seek(14, 1)

            # Read vertices
            positions = []
            for _ in range(vertex_count):
                positions.append(self.read_vec3h())
                self.bs.seek(12, 1)
            self.bs.seek(submesh_end_off)

            # Generate triangles
            triangles = []
            for i in range(vertex_count - 2):
                triangles.append((i, i + 1, i + 2))

            self.submeshes.append(SubMesh(
                submesh_transform,
                positions,
                triangles
            ))
        print("Total vertices:", total_vertex_count)
        
        unk_hash_count = self.read_uint32()
        unk_hashes = [self.read_int32() for _ in range(unk_hash_count)]
