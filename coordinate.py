class Coordinate:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, x, y):
        return Coordinate(self.x + x, self.y + y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
