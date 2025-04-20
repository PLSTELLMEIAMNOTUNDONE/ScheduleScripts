from model.NameAware import NameAware
from model.subjects import Subject


class Group(NameAware):
    def __init__(self, name: str, is_real: bool, volume: int, subjects: list[Subject], sub_groups: list[int] = None):
        super().__init__(name)
        self.is_real = is_real
        self.sub_groups = sub_groups
        self.volume = volume
        self.subjects = subjects
        if self.sub_groups is not None and self.is_real:
            raise Exception("Sub-groups must be none for real group")

    def __str__(self):
        return super().__str__()


