import unittest
from game.game import MonopDealGame
from game.player import RandomPlayer, TerminalPlayer


class TestGame(unittest.TestCase):

    def test_game_terminates(self):
        players = [RandomPlayer('bot1'),
                   RandomPlayer('bot2'),
                   RandomPlayer('bot3'),
                   RandomPlayer('bot4')]
        mdg = MonopDealGame(players)
        winner = mdg.play_game()
        self.assertTrue(winner)
