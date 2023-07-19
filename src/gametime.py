from enum import Enum


class GameStatus(Enum):
    READY = 0
    RUNNING = 1
    FINISHED = 2


class GameTime:
    def __init__(self):
        self.game_time_count = 0
        self.game_end_time = None

    def tick(self):
        self.game_time_count += 1

    def end_game(self):
        if self.game_end_time is None:
            self.game_end_time = self.game_time_count

    def reset(self):
        self.game_time_count = 0
        self.game_end_time = None
