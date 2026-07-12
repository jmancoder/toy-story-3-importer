import struct

from io import BytesIO
from mathutils import Matrix, Vector

class ZReader:
    def __init__(self) -> None:
        self.bs: BytesIO
        self.data_size: int = 0

    def read_matrix(self):
        floats = struct.unpack("<16f", self.bs.read(64))
        return Matrix((
            floats[0:4],
            floats[4:8],
            floats[8:12],
            floats[12:16],
        )).transposed()

    def read_uint16(self) -> int:
        return struct.unpack("<H", self.bs.read(2))[0]
    
    def read_int16(self) -> int:
        return struct.unpack("<h", self.bs.read(2))[0]

    def read_uint32(self) -> int:
        return struct.unpack("<I", self.bs.read(4))[0]

    def read_int32(self) -> int:
        return struct.unpack("<i", self.bs.read(4))[0]

    def read_vec3h(self) -> Vector:
        x, y, z = struct.unpack("<3h", self.bs.read(6))
        return Vector((x / 0x7FFF, y / 0x7FFF, z / 0x7FFF))

    def load_data(self, data: bytes) -> None:
        if len(data) < 4:
            raise RuntimeError("File too short")

        if data[:4].decode("ascii", errors="ignore") == "BFF0":
            # Skip extra header added by the CLI version of BFF
            self.bs = BytesIO(data[16:])
            self.data_size = len(data) - 16
        else:
            self.bs = BytesIO(data)
            self.data_size = len(data)
