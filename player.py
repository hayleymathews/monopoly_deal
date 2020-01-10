import numpy as np


class Player(object):
    """
    basic player implementation
    dumbly picks random actions for now
    """
    def __init__(self, name):
        self.name = name
        self.hand_limit = 7
        self.hand = []

    def choose_action(self):
        return np.random.choice(self.hand + ['end_turn'])

    def discard_cards(self):
        self.hand, discard = self.hand[:7], self.hand[7:]
        return discard

    def draw_cards(self, deck, count):
        self.hand.extend(deck.draw_cards(count))
