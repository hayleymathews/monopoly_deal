import unittest
from game.game import MonopDealGame
from game.player import Player


class TestGame(unittest.TestCase):

    def test_game(self):
        players = [Player('bot1'), Player('bot2'), Player('bot3'), Player('bot4')]
        mdg = MonopDealGame(players, verbose=True)
        winner = mdg.play_game()
        self.assertTrue(winner)
