import numpy as np


class Deck(object):
    """
    basic deck of cards implementation
    reshuffles in discarded cards when draw pile is out
    """

    def __init__(self, cards):
        self.cards = np.random.shuffle(cards)
        self.discards = []

    def draw_cards(self, num_cards):
        try:
            cards, self.cards = self.cards[:num_cards], self.cards[num_cards:]
        except IndexError:
            self.add_discards()
            cards, self.cards = self.cards[:num_cards], self.cards[num_cards:]

        return cards

    def discard_cards(self, cards):
        self.discards.extend(cards)

    def add_discards(self):
        self.cards.extend(np.random.shuffle(self.discards))
