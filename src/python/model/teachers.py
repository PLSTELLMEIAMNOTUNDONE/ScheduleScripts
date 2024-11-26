from model.NameAware import NameAware


class Teacher(NameAware):
    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self):
        return super().__str__() + "\n"



