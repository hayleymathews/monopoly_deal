import numpy as np
from collections import defaultdict

from deck import CARDS, RENTS, money_card, action_card, property_card, rent_card, action_card


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res


class Deck(object):

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


class MonopDealGame(object):

    def __init__(self, players):
        self.players = players
        self.num_players = len(players)
        self.deck = Deck(CARDS)
        self.board = {player: {'bank': [], 'properties': defaultdict(list)} for player in players}
        self.hands = {player: self.deck.draw_cards(5) for player in players}

    def play_card(self, player, card):
        self.hands[player].remove(card)
        self.card_action_map[type(card)](player, card)

    def draw_cards(self, player):
        self.hands[player].extend(self.deck.draw_cards(2))

    @cached_property
    def card_action_map(self):
        return {money_card: self._deposit_money,
                property_card: self._lay_property,
                rent_card: self._collect_rent,
                action_card: lambda x: None
                }

    def _deposit_money(self, player, card):
        self.board[player]['bank'].append(card)

    def _lay_property(self, player, card):
        # TODO: pick which property set card counts for
        self.board[player]['properties'][card.colors[0]].append(card)

    def _collect_rent(self, player, card):
        # TODO: pick which property set to collect rent for
        property_set = card.colors[0]
        rent_level = len(self.board[player]['properties'][property_set])
        if not rent_level:
            return

        rent = RENTS[property_set][rent_level - 1]

        # TODO: pick who to collect from
        other_players = [oplayer for oplayer in self.players if player != oplayer]
        collect_from = other_players if card.players == 'ALL' else other_players[0]

        for victim in collect_from:
            moneys, properties = self._pay_rent(victim, rent)
            [self.deposit_money(player, money) for money in moneys]
            [self.lay_property(player, card, card.colors[0]) for card in properties]

        self.deck.discard_cards([card])

    def show_hand(self, player):
        return self.hands[player]

    def show_board(self):
        for player in self.players:
            print(player)
            print('bank:')
            for mc in self.board[player]['bank']:
                print('  ' + str(mc))
            print('properties:')
            for color, props in self.board[player]['properties'].items():
                print('  ' + color)
                for prop in props:
                    print('    '+ str(prop))
            print()

    def _pay_rent(self, player, amount):
        bank_money = self.board[player]['bank']
        cards, owed, _ = pay_from_bank(bank_money, amount)
        # TODO: start taking properties if you still owe

        for card in cards:
            self.board[player]['bank'].remove(card)

        return cards, []


def pay_from_bank(cards, amount, used_cards=None):
    """
    return cards used, amount still owed, amount paid over
    """
    # TODO: odds i fucked this up real high, write some unit tests
    used_cards = used_cards or []

    if amount <= 0:
        return used_cards, 0, amount

    elif not cards:
        return used_cards, max(amount, 0), 0 - amount

    elif len(cards) == 1:
        return used_cards + cards, max(amount - cards[0].value, 0), 0 - (amount - cards[0].value)

    total_cards_value = sum(card.value for card in cards)
    if amount >= total_cards_value:
        return used_cards + cards, max(amount - total_cards_value, 0), 0 - amount - total_cards_value

    take_options = pay_from_bank(cards[1:], amount - cards[0].value, used_cards + [cards[0]])
    dont_take_options = pay_from_bank(cards[1:], amount, used_cards + [])

    return min(take_options, dont_take_options, key=lambda y: (y[1], -y[2], len(y[0])))
