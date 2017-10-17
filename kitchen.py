class Player:
    def __init__(self, name, cost=0):
        self.name = name
        self.cost = cost


class Case:
    def __init__(self, price, owner=None):
        self.price = price
        self.owner = owner
