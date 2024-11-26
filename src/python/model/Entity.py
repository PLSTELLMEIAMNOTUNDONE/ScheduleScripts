class Entity:
    def __init__(self):
        self.num = None

    def __str__(self):
        return f"id: {str(self.num)}"

    def __repr__(self):
        return self.__str__()

    def set_id(self, num: int):
        if self.num is not None:
            raise Exception(f"перезапись id : {num}")
        self.num = num
