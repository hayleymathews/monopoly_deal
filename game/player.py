import random
from .cards import action_card


class Player(object):
    """
    basic player implementation
    dumbly picks random actions for now
    """
    def __init__(self, name):
        self.name = name
        self.hand_limit = 7
        self.hand = []

    def choose_action(self, actions):
        return random.choice([action for action in actions
                              if not (type(action) == action_card and action.action == 'just say no')])

    def discard_cards(self):
        self.hand, discard = self.hand[:7], self.hand[7:]
        return discard

    def draw_cards(self, deck, count):
        self.hand.extend(deck.draw_cards(count))

    def say_no(self):
        """
        if player has the say no card in their hand, then can play it to stop an action

        Returns:
            bool -- False if passing, say no card if denying
        """
        try:
            say_no_card = next(card for card in self.hand if type(card) == action_card and card.action == 'just say no')
        except StopIteration:
            return False
        if random.choice([True, False]):
            self.hand.remove(say_no_card)
            return say_no_card
        return False
