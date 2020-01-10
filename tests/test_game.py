import unittest
from game.game import MonopDealGame
from game.player import Player


class TestGame(unittest.TestCase):

    def test_game(self):
        players = [Player('bot1'), Player('bot2')]
        mdg = MonopDealGame(players)
        self.assertTrue(mdg.play_game())
