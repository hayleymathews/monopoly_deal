import random
from app import socketio
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

    def write(self, message, channel=None):
        """
        write message to player

        Arguments:
            message {str} -- message to send

        Keyword Arguments:
            channel {str} -- channel to send message to (default: {None})
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
    playable = False

    def write(self, message, channel=None):
        # dont need i/o for bot
        pass

    def read(self, prompt=None):
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


class StrategyPlayer(Player):
    """
    tries to play game with some strategy

    general strategy:
    play money to bank before propety so people wont steal
    play worst properties first
    dont charge rent if you dont have that property
    try to sly deal for a rent card you have
    wait to complete property sets unless you have say nos
    play pass go at start of turn
    """
    playable = False

    def write(self, message, channel=None):
        # dont need i/o for bot
        pass

    def read(self, prompt=None):
        # dont need i/o for bot
        pass

    def choose_action(self, actions):
        return random.choice(self._playable_actions(actions))

    def discard_cards(self):
        pass

    def say_no(self):
        pass


class BotPlayer(Player):
    """
    learns game through RL
    """
    playable = False

    def write(self, message, channel=None):
        # dont need i/o for bot
        pass

    def read(self, prompt=None):
        # dont need i/o for bot
        pass



class PlayablePlayer(Player):
    playable = True

    def choose_action(self, actions):
        playable_actions = self._playable_actions(actions)
        if len(playable_actions) == 1:
            return playable_actions[0]

        # TODO: sloppy af
        message = '\r' + '*' * 80 + '\n'
        message += '\rActions: \n'
        for i, action in enumerate(playable_actions):
            message += '\r\t{}    {} \n'.format(i, action)
        message += '\r' + '*' * 80 + '\n'
        self.write(message)

        valid_action = False
        while not valid_action:
            selected_action = self.read('\renter action # to select: ')
            try:
                action = playable_actions[int(selected_action)]
                valid_action = True
            except Exception:
                self.write('\rinvalid action #, please try again')

        return action

    def discard_cards(self):
        if len(self.hand) <= self.hand_limit:
            return []

        message = '\r' + '*' * 80 + '\n'
        message += '\r\tHand: \n'
        for i, card in enumerate(self.hand):
            message += '\r\t{}    {}\n'.format(i, card)
        message += '\r' + '*' * 80 + '\n'
        self.write(message)

        discard, hand_size = [], len(self.hand)
        while hand_size > self.hand_limit:
            discarded_card = self.read('\renter card # to discard: ')
            try:
                discard.append(self.hand.pop(int(discarded_card) - 1))
                hand_size -= 1
            except Exception:
                self.write('\rinvalid card #, please try again')

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

        use_say_no = self.read('\renter 1 if you wish to use the say no card: ')
        if int(use_say_no) == 1:
            self.hand.remove(say_no_card)
            return say_no_card

        return False


class TerminalPlayer(PlayablePlayer):
    """
    terminal player
    can play locally
    """
    def write(self, message, write_all=False):
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

    def write(self, message, _channel=None):
        self.writer.write(message)

    def read(self, prompt=None):
        return self._get_input(prompt)

    @force_sync
    async def _get_input(self, prompt=None):
        # HACK: have to force this to be blocking so you actually recieve data
        # really shouldn't use an async library to do this, but didnt want to write a telnet service myself
        if prompt:
            self.writer.write(prompt)
        self.reader._eof = False
        x = await self.reader.read(10)
        return x


class WebPlayer(PlayablePlayer):
    """
    web player
    uses sockets to play over the internet
    """
    def __init__(self, name, player_id, socket, namespace, responses):
        super(WebPlayer, self).__init__(name)
        self.player_id = player_id
        self.socket = socket
        self.namespace = namespace
        self.responses = responses

    def write(self, message, channel='player_message'):
        self.socket.emit(channel, {'msg': message}, room=self.player_id, namespace=self.namespace)
        self.socket.sleep(0)

    def read(self, prompt=None):
        if prompt:
            self.socket.emit('prompt', {'msg': prompt}, room=self.player_id, namespace=self.namespace)
            self.socket.sleep()

        # HACK: continuing in the tradition of incredibly lazy implementations
        # the action event that listens to responses from this prompt
        # writes to this shared global response dict, and we just read from it here
        # is it terrible? yes. does it work? occasionally
        resp = self.responses[self.player_id].pop('latest', None)
        while not resp:
            self.socket.sleep()
            resp = self.responses[self.player_id].pop('latest', None)

        # send a signal to client to stop allowing input for this player
        self.socket.emit('end_input', {'msg': ''}, room=self.player_id, namespace=self.namespace)
        return resp
