from model.NameAware import NameAware


class Subject(NameAware):
    def __init__(self, name: str, amount: int, requirements: list[str]):
        super().__init__(name)
        self.amount = amount
        if requirements is None:
           self.requirements = []
        else:
            self.requirements = requirements

    def __str__(self):
        return super().__str__() + f", amount: {self.amount}, requirements: {self.requirements}"
