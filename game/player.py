import random
from .cards import action_card


class Player(object):
    """
    basic player implementation
    """
    def __init__(self, name):
        self.name = name
        self.hand_limit = 7
        self.hand = []

    def __repr__(self):
        return self.name

    def draw_cards(self, deck, count):
        """
        add cards to hand

        Arguments:
            deck {Deck} -- card deck
            count {int} -- number of cards to draw
        """
        self.hand.extend(deck.draw_cards(count))

    def choose_action(self, actions):
        """
        select an action from list provided

        Arguments:
            actions {list} -- some list of actions to choose from
        """
        raise NotImplementedError

    def discard_cards(self):
        """
        discard cards to maintain hand limit
        """
        raise NotImplementedError

    def say_no(self):
        """
        if player has the say no card in their hand, they can play it to stop an action

        Returns:
            bool -- False if passing, say no card if denying
        """
        raise NotImplementedError

    def _say_no_card(self):
        try:
            return next(card for card in self.hand if type(card) == action_card and card.action == 'just say no')
        except StopIteration:
            return False

    def _playable_actions(self, actions):
        return [action for action in actions
                if not (type(action) == action_card and action.action == 'just say no')]


class RandomPlayer(Player):
    """
    randomized player
    dumbly picks actions at random
    """
    def choose_action(self, actions):
        return random.choice(self._playable_actions(actions))

    def discard_cards(self):
        self.hand, discard = self.hand[:self.hand_limit], self.hand[self.hand_limit:]
        return discard

    def say_no(self):
        """
        if player has the say no card in their hand, then can play it to stop an action

        Returns:
            bool -- False if passing, say no card if denying
        """
        say_no_card = self._say_no_card()
        if say_no_card and random.choice([True, False]):
            self.hand.remove(say_no_card)
            return say_no_card
        return False


class TerminalPlayer(Player):
    def choose_action(self, actions):
        playable_actions = self._playable_actions(actions)
        if len(playable_actions) == 1:
            return playable_actions[0]

        print('*' * 100)
        print('\tActions:')
        for i, action in enumerate(playable_actions):
            print('\t{}    {}'.format(i, action))
        print('*' * 100)

        valid_action = False
        while not valid_action:
            selected_action = input('enter action # to select: ')
            try:
                action = playable_actions[int(selected_action)]
                valid_action = True
            except Exception:
                print('invalid action #, please try again')

        return action

    def discard_cards(self):
        if len(self.hand) <= self.hand_limit:
            return []

        print('*' * 100)
        print('\tHand:')
        for i, card in enumerate(self.hand):
            print('\t{}    {}'.format(i, card))
        print('*' * 100)

        discard, hand_size = [], len(self.hand)
        while hand_size > self.hand_limit:
            discarded_card = input('enter card # to discard: ')
            try:
                discard.append(self.hand.pop(int(discarded_card)))
                hand_size -= 1
            except Exception:
                print('invalid card #, please try again')

        return discard

    def say_no(self):
        """
        if player has the say no card in their hand, then can play it to stop an action

        Returns:
            bool -- False if passing, say no card if denying
        """
        say_no_card = self._say_no_card()
        if not say_no_card:
            return False

        use_say_no = input('enter 1 if you wish to use the say no card: ')
        if int(use_say_no) == 1:
            self.hand.remove(say_no_card)
            return say_no_card

        return False
