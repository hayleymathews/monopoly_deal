import random
from .cards import action_card
from .utils import force_sync


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

    def write(self, message):
        """
        write message to player

        Arguments:
            message {str} -- message to send
        """
        raise NotImplementedError

    def read(self, prompt=None):
        """
        receive message from player

        Keyword Arguments:
            prompt {str} -- optional prompt (default: {None})
        """
        raise NotImplementedError

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
    def write(self, message):
        # dont need i/o for bot
        pass

    def read(self):
        # dont need i/o for bot
        pass

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


class PlayablePlayer(Player):
    def choose_action(self, actions):
        playable_actions = self._playable_actions(actions)
        if len(playable_actions) == 1:
            return playable_actions[0]

        message = '*' * 100 + '\n'
        message += '\tActions: \n'
        for i, action in enumerate(playable_actions):
            message += '\t{}    {} \n'.format(i, action)
        message += '*' * 100 + '\n'
        self.write(message)

        valid_action = False
        while not valid_action:
            selected_action = self.read('enter action # to select: ')
            try:
                action = playable_actions[int(selected_action)]
                valid_action = True
            except Exception:
                self.write('invalid action #, please try again')

        return action

    def discard_cards(self):
        if len(self.hand) <= self.hand_limit:
            return []

        message = '*' * 100 + '\n'
        message += '\tHand: \n'
        for i, card in enumerate(self.hand):
            message += '\t{}    {}\n'.format(i, card)
        message += '*' * 100 + '\n'
        self.write(message)

        discard, hand_size = [], len(self.hand)
        while hand_size > self.hand_limit:
            discarded_card = self.read('enter card # to discard: ')
            try:
                discard.append(self.hand.pop(int(discarded_card)))
                hand_size -= 1
            except Exception:
                self.write('invalid card #, please try again')

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

        use_say_no = self.read('enter 1 if you wish to use the say no card: ')
        if int(use_say_no) == 1:
            self.hand.remove(say_no_card)
            return say_no_card

        return False


class TerminalPlayer(PlayablePlayer):
    """
    terminal player
    can play locally
    """
    def write(self, message):
        print(message)

    def read(self, prompt=None):
        return input(prompt)


class TelNetPlayer(PlayablePlayer):
    """
    telnet player
    can play on a remote client
    """
    def __init__(self, name, writer, reader):
        super(TelNetPlayer, self).__init__(name)
        self.writer = writer
        self.reader = reader

    def write(self, message):
        self.writer.write(message)

    def read(self, prompt=None):
        return self._get_input(prompt)

    @force_sync
    async def _get_input(self, prompt=None):
        # HACK: have to force this to be blocking so you actually recieve data
        if prompt:
            self.writer.write(prompt)
        self.reader._eof = False
        x = await self.reader.read(1)
        return x
