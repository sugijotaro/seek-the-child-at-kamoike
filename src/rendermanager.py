import pyxel
import math
import random
from vec2 import Vec2
from gametime import GameStatus


class RenderManager:
    def __init__(self, game):
        self.game = game
        self.played_sound_for_records = False
        self.played_sound_for_instructions = False

    def draw(self):
        pyxel.cls(7)
        self.draw_sky(0, 0, 256, 64)
        self.draw_3d_view(0, 64, 256, 104)
        self.draw_child_indicator(196, 2)
        self.draw_item_indicator(221, 14)
        pyxel.rect(0, 0, 1, 1, 6)

        if self.game.game_status == GameStatus.READY:
            self.draw_ready_status()
        elif self.game.game_status == GameStatus.RUNNING:
            self.draw_running_status()
        elif self.game.game_status == GameStatus.FINISHED:
            self.draw_finished_status()

    def draw_character(self, x, y):
        self.game.player.draw(x, y)
        self.game.player.draw_following_children(
            x, y, self.game.following_counter)

    def draw_map(self, top_left_x, top_left_y, width, height):
        pyxel.blt(top_left_x, top_left_y, 0, 0, 0, width, height, 0)
        pyxel.circ(self.game.player.pos.x, self.game.player.pos.y, 2, 8)
        dir_x_right = self.game.player.pos.x + 10 * \
            math.cos(self.game.player.angle +
                     (self.game.player.fovDeg*math.pi)/360)
        dir_y_right = self.game.player.pos.y + 10 * \
            math.sin(self.game.player.angle +
                     (self.game.player.fovDeg*math.pi)/360)

        pyxel.line(self.game.player.pos.x, self.game.player.pos.y,
                   dir_x_right, dir_y_right, 8)

        for child in self.game.children:
            pyxel.circ(child.pos.x, child.pos.y, 2, 8)

    def draw_child(self, screen_x, screen_y, child_number):
        self.game.children[child_number].draw(screen_x, screen_y)

    def calculate_camera_position(self):
        camera_x = self.game.player.pos.x - self.game.camera_offset * \
            math.cos(self.game.player.angle +
                     (self.game.player.fovDeg*math.pi)/360)
        camera_y = self.game.player.pos.y - self.game.camera_offset * \
            math.sin(self.game.player.angle +
                     (self.game.player.fovDeg*math.pi)/360)
        return Vec2(camera_x, camera_y)

    def draw_pixel(self, pixel_x, pixel_y, player_position, left_endpoint, right_endpoint, horizontal_ratio, vertical_ratio):
        ray_direction = left_endpoint.mul(vertical_ratio * (1 - horizontal_ratio)).add(
            right_endpoint.mul(vertical_ratio * horizontal_ratio))
        target_x = ray_direction.add(player_position).x
        target_y = ray_direction.add(player_position).y
        pyxel.rect(pixel_x, pixel_y, 1, 1,
                   self.game.level.get_tile_color(target_x, target_y))

        for i, child in enumerate(self.game.children):
            child_x_position = child.pos.x
            child_y_position = child.pos.y

            distance_x = abs(child_x_position - target_x)
            distance_y = abs(child_y_position - target_y)
            if child.distance_to_parent is not None:
                threshold = child.distance_to_parent / 10

                if distance_x < threshold and distance_y < threshold:
                    self.draw_child(pixel_x, pixel_y, i)

    def draw_dash_lines(self, top_left_x, top_left_y, width, height):
        line_length = 200
        line_color = 7

        for angle_offset_deg in range(0, 360, 15):
            min_length = random.randint(20, 40)
            angle_offset_rad = math.radians(
                self.game.player.angle + angle_offset_deg)
            line_start_x = top_left_x + width/2 + \
                self.game.player.speed * \
                math.cos(angle_offset_rad) + min_length * \
                math.cos(angle_offset_rad)
            line_start_y = top_left_y + height/2 + \
                self.game.player.speed * \
                math.sin(angle_offset_rad) + min_length * \
                math.sin(angle_offset_rad)
            line_end_x = line_start_x + \
                (line_length - min_length) * math.cos(angle_offset_rad)
            line_end_y = line_start_y + \
                (line_length - min_length) * math.sin(angle_offset_rad)

            pyxel.line(line_start_x, line_start_y,
                       line_end_x, line_end_y, line_color)

    def fv(self, v):
        n = self.game.nearPlane
        return n/(1-v)

    def draw_3d_view(self, top_left_x, top_left_y, width, height):
        pyxel.line(top_left_x, top_left_y + height,
                   top_left_x + width, top_left_y + height, 2)

        player_pos = self.calculate_camera_position()
        player_angle = self.game.player.angle
        left_end_point = Vec2(250, 0).rotate(player_angle)
        right_end_point = left_end_point.rotate(
            (self.game.player.fovDeg*math.pi)/180)

        for pixel_y in range(top_left_y, top_left_y + height):
            for pixel_x in range(top_left_x, top_left_x + width):
                horizontal_ratio = (pixel_x - top_left_x) / width
                vertical_ratio = self.fv(
                    (top_left_y + height - pixel_y + 1e-10) / height)
                self.draw_pixel(pixel_x, pixel_y, player_pos,
                                left_end_point, right_end_point, horizontal_ratio, vertical_ratio)

        character_center_x = top_left_x + width // 2 - 28 // 2
        character_center_y = top_left_y + height // 2 - 41 // 2 + height * 0.1

        self.draw_character(character_center_x, character_center_y)

        if self.game.player.is_dashing:
            self.draw_dash_lines(top_left_x, top_left_y, width, height)

    def draw_sky(self, top_left_x, top_left_y, width, height):
        pyxel.rect(top_left_x, top_left_y, width, height - 38, 6)
        a = self.game.player.angle
        b = a / (math.pi*2)
        c = 512 - b * 512 + 250
        if c > 512:
            c -= 512
        pyxel.blt(top_left_x, top_left_y + height - 38, 0, -c, 218, 256, 38)
        pyxel.blt(top_left_x, top_left_y + height -
                  38, 0, 256 - c, 180, 256, 38)
        pyxel.blt(top_left_x, top_left_y + height -
                  38, 0, 512 - c, 218, 256, 38)

    def draw_child_indicator(self, top_left_x, top_left_y):
        UI_NOTFOUND = (101, 0, 9, 9)
        UI_FOUNDED = (110, 0, 9, 9)
        for i in range(5):
            if self.game.home_counter > i:
                pyxel.blt(top_left_x + 12 * i, top_left_y,
                          1, UI_FOUNDED[0], UI_FOUNDED[1], UI_FOUNDED[2], UI_FOUNDED[3], 6)
            else:
                pyxel.blt(top_left_x + 12 * i, top_left_y,
                          1, UI_NOTFOUND[0], UI_NOTFOUND[1], UI_NOTFOUND[2], UI_NOTFOUND[3], 6)

    def draw_item_indicator(self, top_left_x, top_left_y):
        UI_ITEMUSED = (101, 9, 9, 9)
        UI_ITEM = (110, 9, 9, 9)
        for i in range(3):
            if self.game.player.dash_count > i:
                pyxel.blt(top_left_x + 12 * i, top_left_y,
                          1, UI_ITEMUSED[0], UI_ITEMUSED[1], UI_ITEMUSED[2], UI_ITEMUSED[3], 6)
            else:
                pyxel.blt(top_left_x + 12 * i, top_left_y,
                          1, UI_ITEM[0], UI_ITEM[1], UI_ITEM[2], UI_ITEM[3], 6)

    def draw_centered_text(self, screen_width, y, text, color):
        x = (screen_width - len(text) * 4) / 2
        pyxel.text(x, y, text, color)

    def draw_centered_bordered_text(self, screen_width, y, text, color, border_color=0):
        x = (screen_width - len(text) * 4) / 2
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            pyxel.text(x + dx, y + dy, text, border_color)
        pyxel.text(x, y, text, color)

    def draw_ready_status(self):
        self.draw_centered_text(256, 77, "READY?", pyxel.frame_count % 16)

    def draw_running_status(self):
        if self.game.game_time.game_time_count < 15:
            self.draw_centered_text(256, 77, "GO!", pyxel.frame_count % 16)
        pyxel.text(
            2, 2, f"TIME: {self.game.game_time.game_time_count / 30:.2f}s", 8)

    def draw_finished_status(self):
        top3 = self.game.game_time_manager.load_times()
        self.draw_centered_bordered_text(256, 45, "GAME CLEAR!", 8)
        self.draw_centered_bordered_text(
            256, 55, f'TIME:{self.game.game_time.game_end_time / 30:>7.2f}s', 8)

        if self.game.game_time.game_time_count > self.game.game_time.game_end_time + 30:
            self.draw_centered_bordered_text(256, 70, "- RECORDS -", 8)
            for i in range(3):
                time = f'{top3[i] / 30:>7.2f}s' if i < len(
                    top3) else '   ---  '
                color = pyxel.frame_count % 16 if i < len(
                    top3) and self.game.game_time.game_end_time == top3[i] else 8
                self.draw_centered_bordered_text(
                    256, 80 + i * 10, f'No.{i+1}:{time}', color)

            if not self.played_sound_for_records:
                pyxel.play(3, 6)
                self.played_sound_for_records = True

        if self.game.game_time.game_time_count > self.game.game_time.game_end_time + 60:
            self.draw_centered_bordered_text(256, 120, "press R to restart", 8)
            self.draw_centered_bordered_text(
                256, 130, "press Alt + 1 to take a screenshot", 8)

            if not self.played_sound_for_instructions:
                pyxel.play(3, 6)
                self.played_sound_for_instructions = True
