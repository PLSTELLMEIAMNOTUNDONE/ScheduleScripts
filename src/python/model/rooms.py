from model.NameAware import NameAware


class Room(NameAware):
    def __init__(self, name: str, capacity: int, features: list[str]):
        super().__init__(name)
        self.capacity = capacity
        if features is None:
            self.features = []
        else:
            self.features = features

    def __str__(self):
        return super().__str__() + f", capacity: {self.capacity}, features: {self.features}"
