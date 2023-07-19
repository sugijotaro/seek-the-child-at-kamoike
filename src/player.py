import pyxel
import math
from vec2 import Vec2

FORWARD_KEY = pyxel.KEY_W
BACKWARD_KEY = pyxel.KEY_S
LEFT_KEY = pyxel.KEY_A
RIGHT_KEY = pyxel.KEY_D
DASH_KEY = pyxel.KEY_SPACE
DASH_TIMER_LIMIT = 30
DASH_COUNT_LIMIT = 3
SPEED_BOOST_WHILE_DASHING = 2
SPEED_REDUCTION_WHILE_BACKWARDS = 0.3
UNDERWATER_TURN_ANGLE = math.pi/180
LAND_TURN_ANGLE = math.pi/180 * 3
FRAME_DURATION = 8
LEVEL_BOUNDARY = 0


class Player:
    HEAD1 = (0, 0, 28, 20)
    BODY1 = (0, 20, 28, 17)
    FOOT1_1 = (0, 37, 28, 6)
    FOOT1_2_A = (0, 43, 28, 6)
    FOOT1_3_A = (0, 49, 28, 6)
    FOOT1_2_B = (0, 55, 28, 6)
    FOOT1_3_B = (0, 61, 28, 6)
    HEAD2 = (28, 0, 28, 20)
    BODY2 = (28, 20, 28, 16)
    FOOT2_1_A = (28, 36, 28, 7)
    FOOT2_2_A = (28, 43, 28, 7)
    FOOT2_1_B = (28, 50, 28, 7)
    FOOT2_2_B = (28, 57, 28, 7)
    CHILD_BACK = (90, 0, 11, 18)

    def __init__(self):
        self.pos = Vec2(40, 32)
        self.angle = 0.915
        self.speed = 0.5
        self.is_moving = False
        self.is_looking_left = False
        self.is_looking_right = False
        self.is_underwater = False
        self.fovDeg = 75
        self.dash_count = 0
        self.is_dashing = False
        self.dash_timer = 0

    def move_player(self, level_width, level_height):
        self.is_looking_left = False
        self.is_looking_right = False

        if self.is_dashing:
            self.is_moving = True
            self.speed *= 2
            self.dash_timer += 1

            if self.dash_timer >= DASH_TIMER_LIMIT:
                self.is_dashing = False
                self.dash_timer = 0

            self.pos.x += self.speed * \
                math.cos(self.angle + (self.fovDeg*math.pi)/360)
            self.pos.y += self.speed * \
                math.sin(self.angle + (self.fovDeg*math.pi)/360)
        else:
            if pyxel.btn(FORWARD_KEY):
                self.is_moving = True
                self.pos.x += self.speed * \
                    math.cos(self.angle + (self.fovDeg*math.pi)/360)
                self.pos.y += self.speed * \
                    math.sin(self.angle + (self.fovDeg*math.pi)/360)
            else:
                self.is_moving = False

            if pyxel.btn(BACKWARD_KEY):
                self.is_moving = True
                self.speed *= 0.3
                self.pos.x -= self.speed * \
                    math.cos(self.angle + (self.fovDeg*math.pi)/360)
                self.pos.y -= self.speed * \
                    math.sin(self.angle + (self.fovDeg*math.pi)/360)

            if pyxel.btn(LEFT_KEY) and not self.is_dashing:
                if self.is_underwater:
                    self.angle -= math.pi/180
                else:
                    self.angle -= math.pi/180 * 3
                self.is_looking_left = True
                self.is_looking_right = False
                self.is_moving = True

            if pyxel.btn(RIGHT_KEY) and not self.is_dashing:
                if self.is_underwater:
                    self.angle += math.pi/180
                else:
                    self.angle += math.pi/180 * 3
                self.is_looking_right = True
                self.is_looking_left = False
                self.is_moving = True

        if pyxel.btnp(DASH_KEY) and not self.is_dashing and self.dash_count < DASH_COUNT_LIMIT:
            self.is_dashing = True
            pyxel.play(3, 4)
            self.dash_count += 1

        self.angle = self.angle % (2 * math.pi)
        if self.angle < 0:
            self.angle += 2 * math.pi

        self.pos.x = max(min(self.pos.x, level_width), 0)
        self.pos.y = max(min(self.pos.y, level_height), 0)

    def draw(self, x, y):
        direction = 'left' if self.is_looking_left else 'right' if self.is_looking_right else None
        blt_direction = -28 if direction == 'right' else 28
        head = self.HEAD2 if direction else self.HEAD1
        body = self.BODY2 if direction else self.BODY1
        foot_pos = y + 34 if direction else y + 35

        if pyxel.frame_count // 24 % 2 == 0:
            pyxel.blt(x, y, 1, head[0], head[1], blt_direction, head[3], 6)
        else:
            pyxel.blt(x, y + 1, 1, head[0], head[1], blt_direction, head[3], 6)

        pyxel.blt(x, y + 18, 1, body[0], body[1], blt_direction, body[3], 6)

        if self.is_moving and self.is_underwater:
            if pyxel.frame_count // 8 % 2 == 0:
                foot = self.FOOT2_1_B if direction else self.FOOT1_2_B
            else:
                foot = self.FOOT2_2_B if direction else self.FOOT1_3_B
        elif self.is_moving and not self.is_underwater:
            if pyxel.frame_count // 8 % 2 == 0:
                foot = self.FOOT2_1_A if direction else self.FOOT1_2_A
            else:
                foot = self.FOOT2_2_A if direction else self.FOOT1_3_A
        elif not self.is_moving and self.is_underwater:
            if pyxel.frame_count // 8 % 2 == 0:
                foot = self.FOOT1_2_B
            else:
                foot = self.FOOT1_3_B
        elif not self.is_moving and not self.is_underwater:
            foot = self.FOOT1_1
        else:
            if self.frame // 8 % 2 == 0:
                foot = self.FOOT2_1_A if direction else self.FOOT1_2_A
            else:
                foot = self.FOOT2_2_A if direction else self.FOOT1_3_A

        pyxel.blt(x, foot_pos, 1, foot[0], foot[1], blt_direction, foot[3], 6)

    def draw_following_children(self, x, y, following_counter):
        if following_counter == 1:
            pyxel.blt(
                x + 8, y+30, 1, self.CHILD_BACK[0], self.CHILD_BACK[1], self.CHILD_BACK[2], self.CHILD_BACK[3], 6)
        elif following_counter >= 2:
            pyxel.blt(
                x + 4, y+30, 1, self.CHILD_BACK[0], self.CHILD_BACK[1], self.CHILD_BACK[2], self.CHILD_BACK[3], 6)
            pyxel.blt(
                x + 13, y+30, 1, self.CHILD_BACK[0], self.CHILD_BACK[1], self.CHILD_BACK[2], self.CHILD_BACK[3], 6)
        if following_counter >= 3:
            pyxel.blt(
                x + 4, y+35, 1, self.CHILD_BACK[0], self.CHILD_BACK[1], self.CHILD_BACK[2], self.CHILD_BACK[3], 6)
        if following_counter >= 4:
            pyxel.blt(
                x + 13, y+35, 1, self.CHILD_BACK[0], self.CHILD_BACK[1], self.CHILD_BACK[2], self.CHILD_BACK[3], 6)
        if following_counter >= 5:
            pyxel.blt(
                x + 8, y+40, 1, self.CHILD_BACK[0], self.CHILD_BACK[1], self.CHILD_BACK[2], self.CHILD_BACK[3], 6)
