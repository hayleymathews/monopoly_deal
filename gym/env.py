import gym
from gym import error, spaces, utils
from gym.utils import seeding

from game.game import MonopDealGame
from game.player import RandomPlayer, BotPlayer


class MonopEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, num_players=3):
        self.num_players = num_players
        self.game = None

        self.seed()
        self.reset()

    def step(self, action):
        # question here:
        # is it valid to pass in all 3 actions a bot might take at once
        # or should each step be an action taken
        # also how the fuck to handle saying no?
        

        current_score = self.game.scores['bot']
        # somehow play a round where each player takes a turn
        winner = self.game.play_round()

        reward = self.game.scores['bot'] - current_score

        observations = self._get_observation_space() if not winner else None

        return observations, reward, bool(winner), {}

    def reset(self):
        players = [RandomPlayer(f"rand {num}") for num in self.num_players] + [BotPlayer('bot')]
        self.game = MonopDealGame(players)
        pass

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    def _get_observation_space(self):
        pass
