import unittest
from game.game import MonopDealGame
from game.player import RandomPlayer, TerminalPlayer


class TestGame(unittest.TestCase):

    # def test_game(self):
    #     players = [RandomPlayer('bot1'),
    #                RandomPlayer('bot2'),
    #                RandomPlayer('bot3'),
    #                RandomPlayer('bot4')]
    #     mdg = MonopDealGame(players, verbose=True)
    #     winner = mdg.play_game()
    #     self.assertTrue(winner)
    
    def test_game(self):
        players = [RandomPlayer('bot1'),
                   TerminalPlayer('hayley')]
        mdg = MonopDealGame(players, verbose=True)
        winner = mdg.play_game()
        self.assertTrue(winner)
