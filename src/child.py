import pyxel
from vec2 import Vec2


class Child:
    HEAD1 = (56, 0, 17, 18)
    HEAD2 = (73, 0, 17, 18)
    BODY1 = (56, 18, 20, 22)
    BODY2 = (76, 18, 20, 22)
    MIN1 = (56, 40, 19, 19)
    MIN2 = (75, 40, 19, 19)

    def __init__(self, start_pos, end_pos):
        self.start_pos = Vec2(start_pos[0], start_pos[1])
        self.end_pos = Vec2(end_pos[0], end_pos[1])
        self.pos = self.start_pos.copy()
        self.speed = 1
        self.following = False
        self.at_home = False
        self.target = self.end_pos
        self.has_been_drawn = False
        self.distance_to_parent = None

    def update(self, player_pos):
        if not self.following and not self.at_home:
            if self.pos.sub(self.target).mag() < self.speed:
                self.target = self.start_pos if self.target.equals(
                    self.end_pos) else self.end_pos
            self.move_towards(self.target)
        elif self.following:
            self.move_towards(player_pos)

    def move_towards(self, target_pos):
        direction = target_pos.sub(self.pos).norm()
        self.pos = self.pos.add(direction.mul(self.speed))

    def draw(self, screen_x, screen_y):
        if self.has_been_drawn or self.following:
            return

        if self.distance_to_parent > 120:
            pyxel.rect(screen_x, screen_y - 1, 1, 1, 10)
        elif self.distance_to_parent > 80:
            pyxel.rect(screen_x, screen_y - 3, 3, 3, 10)
        elif self.distance_to_parent > 50:
            pyxel.rect(screen_x, screen_y - 5, 5, 5, 10)
        elif self.distance_to_parent > 40:
            x = screen_x - 19 / 2
            y = screen_y - 19
            if pyxel.frame_count // 24 % 2 == 0:
                pyxel.blt(
                    x, y, 1, self.MIN1[0], self.MIN1[1], self.MIN1[2], self.MIN1[3], 6)
            else:
                pyxel.blt(
                    x, y, 1, self.MIN2[0], self.MIN2[1], self.MIN2[2], self.MIN2[3], 6)
        else:
            x = screen_x - 39 / 2
            y = screen_y - 35
            if pyxel.frame_count // 24 % 2 == 0:
                pyxel.blt(
                    x, y + 13, 1, self.BODY1[0], self.BODY1[1], self.BODY1[2], self.BODY1[3], 6)
                pyxel.blt(
                    x + 19, y + 13, 1, self.BODY1[0], self.BODY1[1], -self.BODY1[2], self.BODY1[3], 6)
            else:
                pyxel.blt(
                    x, y + 13, 1, self.BODY2[0], self.BODY2[1], self.BODY2[2], self.BODY2[3], 6)
                pyxel.blt(
                    x + 19, y + 13, 1, self.BODY2[0], self.BODY2[1], -self.BODY2[2], self.BODY2[3], 6)

            if pyxel.frame_count // 24 % 2 == 0:
                pyxel.blt(
                    x + 11, y + 1, 1, self.HEAD1[0], self.HEAD1[1], self.HEAD1[2], self.HEAD1[3], 6)
            else:
                pyxel.blt(
                    x + 11, y, 1, self.HEAD2[0], self.HEAD2[1], self.HEAD2[2], self.HEAD2[3], 6)

        self.has_been_drawn = True
