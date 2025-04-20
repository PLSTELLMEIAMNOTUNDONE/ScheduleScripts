from model.Entity import Entity


class Event(Entity):
    def __init__(self, num: int, g: int, r: int, s: int, t: int):
        super().__init__()
        super().set_id(num)
        self.g = g
        self.r = r
        self.s = s
        self.t = t
    def __str__(self):
        return super().__str__() + f'(g: {self.g}, r: {self.r}, s: {self.s}, t: {self.t})'


