import numpy as np
from collections import defaultdict, namedtuple

from card import CARDS, RENTS, money_card, action_card, property_card, rent_card, action_card
from deck import Deck
from utils import pay_from_bank, pay_from_properties, check_full_set, get_rent, cached_property


class MonopDealGame(object):

    def __init__(self, players):
        self.players = players
        self.rent_level = 1  # TODO: sloppy
        self.deck = Deck(CARDS)
        self.board = {player.name: {'bank': [], 'properties': defaultdict(list)} for player in self.players}
        [player.draw_cards(self.deck, 5) for player in self.players]

    def play_game(self):
        winner = False
        rounds = 0  # TODO: write some tests, make sure this terminates
        while not winner and rounds < 1000:
            winner = self.play_round()
            rounds += 1
        return winner

    def play_round(self):
        for player in self.players:
            self.take_turn(player)
            self.show_board()
            winner = self.check_win_condition()
            if winner:
                return winner

    def take_turn(self, player):
        self.rent_level = 1
        player.draw_cards(self.deck, 2)
        actions = 3
        while actions:
            actions -= 1
            card = player.choose_action()
            if card == 'end_turn':
                break
            self._play_card(player, card)
        self.deck.discard_cards(player.discard_cards())

    def check_win_condition(self):
        for player in self.players:
            full_sets = [prop_set for prop_set, properties in self.board[player.name]['properties'].items()
                         check_full_set(prop_set, properties)]
            if len(full_sets) >= 3:
                return player
        return False

    def _play_card(self, player, card):
        player.hand.remove(card)
        self._card_map[type(card)](player, card)

    @cached_property
    def _card_map(self):
        return {money_card: self._deposit_money,
                property_card: self._lay_property,
                rent_card: self._collect_rent,
                action_card: self._do_action,
                }

    def _deposit_money(self, player, card):
        self.board[player.name]['bank'].append(card)

    def _lay_property(self, player, card):
        # TODO: pick which property set card counts for
        self.board[player.name]['properties'][card.colors[0]].append(card)

    def _collect_rent(self, player, card):
        # TODO: pick which property set to collect rent for
        property_set = card.colors[0]
        rent_level = len(self.board[player.name]['properties'][property_set])
        if not rent_level:
            return

        rent = get_rent(property_set, properties) * self.rent_level

        # TODO: pick who to collect from
        other_players = [oplayer for oplayer in self.players if player != oplayer]
        collect_from = other_players if card.players == 'ALL' else [other_players[0]]
        self._collect_money(player, rent, collect_from)

        self.deck.discard_cards([card])

    def _collect_money(self, collector, amount_owed, payers):
        for payer in payers:
            moneys, properties = self._pay(payer, amount_owed)
            [self._deposit_money(collector, money) for money in moneys]
            [self._lay_property(collector, card) for card in properties]

    def _do_action(self, player, card):
        if card.action == 'debt_collector':
            # TODO: pick who to collect from
            collect_from = [[oplayer for oplayer in self.players if player != oplayer][0]]
            self._collect_money(player, 5000000, collect_from)
        elif card.action == 'it\'s my birthday':
            collect_from = [oplayer for oplayer in self.players if player != oplayer]
            self._collect_money(player, 2000000, collect_from)
        elif card.action == 'pass go':
            player.draw_cards(self.deck, 2)

        # TODO: other action cards

        self.deck.discard_cards([card])

    def show_hand(self, player):
        return player.hand

    def show_board(self):
        # TODO: better repr
        for player in self.players:
            print(player.name)
            print('bank:')
            for mc in self.board[player.name]['bank']:
                print('  ' + str(mc))
            print('properties:')
            for color, props in self.board[player.name]['properties'].items():
                print('  ' + color)
                if len(props) == len(RENTS[color]):
                    print('  ' + '************')
                for prop in props:
                    print('    ' + str(prop))
            print()

    def _pay(self, player, amount):
        bank_payment = pay_from_bank(amount, self.board[player.name]['bank'],)
        self.board[player.name]['bank'] = bank_payment.remaining

        if not bank_payment.owed:
            return bank_payment.paid, []

        # start taking properties if you still owe money
        property_payment = pay_from_properties(bank_payment.owed, self.board[player.name]['properties'])
        # TODO: sloppy
        self.board[player.name]['properties'] = defaultdict(list)
        [self._lay_property(player, card) for card in property_payment.remaining]

        return bank_payment.paid, property_payment.paid
