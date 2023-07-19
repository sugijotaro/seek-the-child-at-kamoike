import pyxel
import json
from vec2 import Vec2
from gametime import GameTime
from gametime import GameStatus
from level import Level
from player import Player
from child import Child
from gametimemanager import GameTimeManager
from rendermanager import RenderManager

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 168
LEVEL_WIDTH = 255
LEVEL_HEIGHT = 179
NEAR_PLANE = 0.03
CAMERA_OFFSET = 8
CHILDREN_POSITIONS = [
    Child((100, 142), (120, 142)),
    Child((25, 118), (38, 143)),
    Child((140, 58), (161, 41)),
    Child((222, 42), (231, 71)),
    Child((223, 124), (208, 145))
]
PLAYER_BASE_SPEED = 0.6
PLAYER_SPEED_LIMIT = 0.2
PLAYER_SPEED_REDUCTION_PER_CHILD = 0.03


class Game:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, "Seek the Child at Kamoike")
        pyxel.load("game_resources.pyxres")
        with open("music.json", "rt") as f:
            self.music = json.loads(f.read())
        pyxel.sound(3).set(notes='C3G4G4', tones='TT',
                           volumes='33', effects='NN', speed=10)
        pyxel.sound(4).set(notes='D4E4F4G4A4B4B4B4B4B4', tones='TT',
                           volumes='33', effects='NN', speed=10)
        pyxel.sound(5).set(notes='B4B4E3B3', tones='TT',
                           volumes='33', effects='NN', speed=10)
        pyxel.sound(6).set(notes='A3A4', tones='TT',
                           volumes='33', effects='NN', speed=10)

        self.nearPlane = NEAR_PLANE
        self.camera_offset = CAMERA_OFFSET

        self.player = Player()
        self.level = Level(LEVEL_WIDTH, LEVEL_HEIGHT)
        self.children = CHILDREN_POSITIONS

        self.home_counter = 0
        self.following_counter = 0
        self.game_time = GameTime()
        self.game_status = GameStatus.READY
        self.game_time_manager = GameTimeManager()

        self.render_manager = RenderManager(self)

        pyxel.run(self.update, self.render_manager.draw)

    def restart(self):
        self.game_status = GameStatus.READY
        self.game_time.reset()
        self.player = Player()
        self.level = Level(256, 179)
        self.children = [
            Child((100, 142), (120, 142)),
            Child((25, 118), (38, 143)),
            Child((140, 58), (161, 41)),
            Child((222, 42), (231, 71)),
            Child((223, 124), (208, 145))
        ]
        self.home_counter = 0
        self.following_counter = 0
        pyxel.stop()

    def update(self):
        if self.game_status == GameStatus.READY:
            self.game_status_ready()
        elif self.game_status == GameStatus.RUNNING:
            if pyxel.play_pos(0) is None:
                for ch, sound in enumerate(self.music):
                    if ch < 3:
                        pyxel.sound(ch).set(*sound)
                        pyxel.play(ch, ch, loop=True)
            self.game_status_running()
        elif self.game_status == GameStatus.FINISHED:
            self.game_status_finished()

    def update_player(self):
        self.player.speed = max(
            PLAYER_SPEED_LIMIT,
            PLAYER_BASE_SPEED - PLAYER_SPEED_REDUCTION_PER_CHILD * self.following_counter ** 2
        )
        self.player.move_player(self.level.width, self.level.height)
        self.player.is_underwater = self.level.is_underwater(self.player.pos)

    def update_children(self):
        for child in self.children:
            child.update(self.player.pos)
            child.distance_to_parent = child.pos.sub(self.player.pos).mag()
            if not child.following and not child.at_home and child.pos.sub(self.player.pos).mag() < 5:
                child.following = True
                pyxel.play(3, 3)
                self.following_counter += 1

            if child.following and self.level.is_in_home(self.player.pos):
                child.following = False
                child.at_home = True
                child.pos = Vec2(*self.level.HOME_POSITIONS[self.home_counter])
                pyxel.play(3, 5)
                self.home_counter += 1
                self.following_counter -= 1

    def process_update(self):
        self.update_player()
        self.update_children()

    def reset_draw_state(self):
        for child in self.children:
            child.has_been_drawn = False

    def game_status_ready(self):
        self.game_time.tick()
        if self.game_time.game_time_count > 30:
            self.game_status = GameStatus.RUNNING
            self.game_time.game_time_count -= 30

    def game_status_running(self):
        self.process_update()
        self.reset_draw_state()
        self.game_time.tick()
        if self.home_counter >= 5:
            self.game_status = GameStatus.FINISHED
            self.game_time.end_game()
            self.game_time_manager.add_time(self.game_time.game_time_count)
            self.game_time_manager.save_times()
            print("Top 3 times:", self.game_time_manager.load_times())

    def game_status_finished(self):
        self.process_update()
        self.reset_draw_state()
        self.game_time.tick()
        if pyxel.btnp(pyxel.KEY_R):
            self.restart()
