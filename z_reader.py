import struct

from io import BytesIO
from mathutils import Matrix

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

    def read_uint8(self) -> int:
        return int.from_bytes(self.bs.read(1),
            byteorder="little", signed=False)
    
    def read_int8(self) -> int:
        return int.from_bytes(self.bs.read(1),
            byteorder="little", signed=True)

    def read_uint16(self) -> int:
        return int.from_bytes(self.bs.read(2),
            byteorder="little", signed=False)

    def read_int16(self) -> int:
        return int.from_bytes(self.bs.read(2),
            byteorder="little", signed=True)

    def read_uint24(self) -> int:
        return int.from_bytes(self.bs.read(3),
            byteorder="little", signed=False)
    
    def read_int24(self) -> int:
        return int.from_bytes(self.bs.read(3),
            byteorder="little", signed=True)

    def read_uint32(self) -> int:
        return int.from_bytes(self.bs.read(4),
            byteorder="little", signed=False)

    def read_int32(self) -> int:
        return int.from_bytes(self.bs.read(4),
            byteorder="little", signed=True)

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
