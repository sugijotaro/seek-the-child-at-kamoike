import math


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, vec):
        return Vec2(self.x + vec.x, self.y + vec.y)

    def sub(self, vec):
        return Vec2(self.x - vec.x, self.y - vec.y)

    def mul(self, scalar):
        return Vec2(scalar * self.x, scalar * self.y)

    def div(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def dot(self, vec):
        return self.x * vec.x + self.y * vec.y

    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def rotate(self, rad):
        return Vec2(
            self.x * math.cos(rad) - self.y * math.sin(rad),
            self.x * math.sin(rad) + self.y * math.cos(rad)
        )

    def norm(self):
        return self.mul(1 / self.mag())

    def copy(self):
        return Vec2(self.x, self.y)

    def equals(self, vec):
        return self.x == vec.x and self.y == vec.y
