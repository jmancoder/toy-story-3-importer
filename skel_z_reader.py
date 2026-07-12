from mathutils import Matrix
from .z_reader import ZReader


class SkelZReader(ZReader):
    def __init__(self) -> None:
        super().__init__()
        self.bone_count: int = 0
        self.bone_names: list[str] = []
        self.bone_matrices: list[Matrix] = []
        self.bone_parent_ids: list[int] = []

    def load_data(self, data: bytes) -> None:
        super().load_data(data)

        self.bs.seek(0x30)
        bone_count = self.read_uint32()
        for _ in range(bone_count):
            self.bs.seek(164, 1)
            self.bone_matrices.append(self.read_matrix())
            self.bone_parent_ids.append(self.read_int32())
            self.read_int32()
            self.read_int32()
            self.read_int32()
            self.bone_names.append(str(self.read_int32()))
