import json
import os


class GameTimeManager:
    def __init__(self, filepath='game_times.json'):
        self.filepath = filepath
        if not os.path.isfile(filepath):
            self.game_times = []
        else:
            with open(filepath, 'r') as file:
                self.game_times = json.load(file)

    def add_time(self, time):
        self.game_times.append(time)
        self.game_times.sort()

    def save_times(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.game_times, file)

    def load_times(self):
        with open(self.filepath, 'r') as file:
            self.game_times = json.load(file)
        return self.game_times[:3] if len(self.game_times) > 3 else self.game_times
