import numpy as np
from collections import defaultdict

from .cards import CARDS, money_card, action_card, property_card, rent_card, action_card
from .deck import Deck
from .board import Board
from .utils import pay_from_bank, pay_from_properties, check_full_set, get_rent, cached_property


class MonopDealGame(object):

    def __init__(self, players):
        self.players = players
        self.rent_level = 1  # TODO: sloppy
        self.deck = Deck(CARDS)
        self.board = Board(players)
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
            player.hand.remove(card)
            self._card_map[type(card)](player, card)
        self.deck.discard_cards(player.discard_cards())

    def check_win_condition(self):
        for player in self.players:
            full_sets = [prop_set for prop_set, properties in self.board.properties(player).items()
                         if check_full_set(prop_set, properties)]
            if len(full_sets) >= 3:
                return player
        return False

    @cached_property
    def _card_map(self):
        return {money_card: self._deposit_money,
                property_card: self._lay_property,
                rent_card: self._collect_rent,
                action_card: self._do_action,
                }

    def _deposit_money(self, player, card):
        self.board.bank(player).append(card)

    def _lay_property(self, player, card):
        # TODO: pick which property set card counts for
        self.board.properties(player)[card.colors[0]].append(card)

    def _collect_rent(self, player, card):
        # TODO: pick which property set to collect rent for
        property_set = card.colors[0]
        rent = get_rent(property_set, self.board.properties(player)[property_set]) * self.rent_level
        if not rent:
            return

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

    def _pay(self, player, amount):
        bank_payment = pay_from_bank(amount, self.board.bank(player))
        self.board.reset_bank(player, bank_payment.remaining)

        if not bank_payment.owed:
            return bank_payment.paid, []

        # start taking properties if you still owe money
        property_payment = pay_from_properties(bank_payment.owed, self.board.properties(player))

        # TODO: sloppy
        self.board.reset_properties(player)
        [self._lay_property(player, card) for card in property_payment.remaining]

        return bank_payment.paid, property_payment.paid
