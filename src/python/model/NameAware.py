from model.Entity import Entity


class NameAware(Entity):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return super().__str__() + f", name: {self.name}"
