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
            card = player.choose_action(player.hand + ['end turn'])
            if card == 'end turn':
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
        property_set = player.choose_action(card.colors)
        self.board.properties(player)[property_set].append(card)

    def _collect_rent(self, player, card):
        property_set = player.choose_action(card.colors)
        rent = get_rent(property_set, self.board.properties(player)[property_set]) * self.rent_level
        if not rent:
            return

        other_players = self.other_players(player)
        collect_from = other_players if card.players == 'ALL' else [player.choose_action(other_players)]
        self._collect_money(player, rent, collect_from)

        self.deck.discard_cards([card])

    def _collect_money(self, collector, amount_owed, payers):
        for payer in payers:
            say_no_card = payer.say_no()
            if say_no_card:
                self.deck.discard_cards([say_no_card])
                continue

            moneys, properties = self._pay(payer, amount_owed)
            [self._deposit_money(collector, money) for money in moneys]
            [self._lay_property(collector, card) for card in properties]

    def _do_action(self, player, card):
        if card.action == 'debt_collector':
            collect_from = [player.choose_action(self.other_players(player))]
            self._collect_money(player, 5000000, collect_from)
        elif card.action == 'it\'s my birthday':
            collect_from = self.other_players(player)
            self._collect_money(player, 2000000, collect_from)
        elif card.action == 'pass go':
            player.draw_cards(self.deck, 2)
        elif card.action == 'deal breaker':
            self._steal_property_set(player, full_sets=True)
        elif card.action == 'sly deal':
            self._steal_property_set(player, full_sets=False)
        elif card.action == 'forced deal':
            self._steal_property_set(player, full_sets=False, swap=True)
        elif card.action == 'house':
            pass
        elif card.action == 'hotel':
            pass

        # TODO: other action cards

        self.deck.discard_cards([card])

    def other_players(self, player):
        return [x for x in self.players if x != player]

    def _steal_property_set(self, player, full_sets=False, swap=False):
        other_players = self.other_players(player)
        if full_sets:
            sets = [(victim, prop_set, properties) for victim in other_players
                    for prop_set, properties in self.board.properties(victim).items()
                    if victim != player and check_full_set(prop_set, properties)]
        else:
            sets = [(victim, prop_set, [prop]) for victim in other_players
                    for prop_set, properties in self.board.properties(victim).items()
                    if victim != player and not check_full_set(prop_set, properties)
                    for prop in properties]
        if not sets:
            return

        if swap:
            player_sets = [(prop_set, [prop]) for prop_set, properties in self.board.properties(player).items()
                           if not check_full_set(prop_set, properties)
                           for prop in properties]
            if not player_sets:
                return

        victim, prop_set, properties = player.choose_action(sets)
        say_no_card = victim.say_no()
        if say_no_card:
            self.deck.discard_cards([say_no_card])
            return

        self.board.reset_properties(victim, prop_set, properties)
        [self._lay_property(player, prop) for prop in properties]

        if swap:
            swap_set, swap_props = player.choose_action(player_sets)
            self.board.reset_properties(player, swap_set, swap_props)
            [self._lay_property(victim, prop) for prop in swap_props]

    def _pay(self, player, amount):
        # try to pay debt off using money in the bank first
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