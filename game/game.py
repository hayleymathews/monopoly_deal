from collections import defaultdict

import numpy as np

from .board import Board
from .cards import (CARDS, END_TURN, SHOW_BOARD, REARRANGE_PROPS, action_card, money_card,
                    property_card, rent_card)
from .deck import Deck
from .utils import (cached_property, check_full_set, get_rent, pay_from_bank,
                    pay_from_properties)


class MonopDealGame(object):
    """
    like the regular monopoly game, proof that capitalism is a bit evil
    but unlike regular monopoly, this one eventually ends (possibly in tears)
    """

    def __init__(self,
                 players,
                 verbose=False):
        """
        set up md game

        Arguments:
            players {list} -- list of Player instances

        Keyword Arguments:
            verbose {bool} -- print a bunch of game state throughout (default: {False})
        """
        self.players = players
        self.verbose = verbose
        self.rent_level = 1  # TODO: sloppy
        self.deck = Deck(CARDS)
        self.board = Board(players)
        self.free_actions = [REARRANGE_PROPS, SHOW_BOARD, END_TURN]
        [player.draw_cards(self.deck, 5) for player in self.players]

    def play_game(self):
        """
        play a complete game until a player has won

        Returns:
            Player -- winning player
        """
        winner = False
        rounds = 0  # TODO: write some tests, make sure this terminates
        while not winner and rounds < 1000:
            winner = self.play_round()
            rounds += 1
        self._write_players('\rWinner: {} in {} rounds\n'.format(winner.name, rounds))
        return winner

    def play_round(self):
        """
        play a round where each player takes a turn

        Returns:
            bool -- Player if winner, else None
        """
        for player in self.players:
            self.take_turn(player)
            winner = self._check_win_condition()
            if winner:
                return winner

    def take_turn(self,
                  player):
        """
        in each turn a player must:
            1) draw 2 cards
            2) play up to 3 cards from their hand
            3) discard cards to maintain hand limit of 7

        Arguments:
            player {Player} -- player instance
        """
        self.rent_level, actions = 1, 3
        player.draw_cards(self.deck, 2)

        while actions:
            cards = player.hand + self.free_actions if player.playable else player.hand
            card = player.choose_action(cards)

            self._write_players("\r{} played {}\n\r".format(player.name, card))

            if card == END_TURN:
                break
            elif card == SHOW_BOARD:
                self._write_players(self.board.show_board(), [player], board=True)
            elif card == REARRANGE_PROPS:
                self._rearrange_properties(player)

            else:
                actions -= 1
                player.hand.remove(card)
                self._card_map[type(card)](player, card)

        self.deck.discard_cards(player.discard_cards())
        self._write_players(self.board.show_board(), board=True)

    def _check_win_condition(self):
        """
        to win a game a player must have 3 full property sets

        Returns:
            bool -- Player if winner, else False
        """
        for player in self.players:
            full_sets = [prop_set for prop_set, properties in self.board.properties(player).items()
                         if check_full_set(prop_set, properties)]
            if len(full_sets) >= 3:
                return player
        return False

    #
    # Card Options
    #
    @cached_property
    def _card_map(self):
        return {money_card: self._deposit_money,
                property_card: self._lay_property,
                rent_card: self._collect_rent,
                action_card: self._do_action,
                }

    def _deposit_money(self,
                       player,
                       card):
        """
        put money in bank for player

        Arguments:
            player {Player} -- player getting money
            card {money_card} -- money
        """
        self.board.bank(player).append(card)

    def _lay_property(self,
                      player,
                      card,
                      property_set=None):
        """
        place property on board for player
        where it can now:
            count towards being a property set
            have rent collected on it
            be stolen by another player ...

        Arguments:
            player {Player} -- player playing property
            card {property_card} -- property

        Keyword Arguments:
            property_set {str} -- prop set to play property for (default: {None})
        """
        if type(card) == action_card:
            # TODO: hacky as shit, handle this elsewhere
            self._lay_bonus_property(player, card)
        else:
            property_set = property_set or player.choose_action(card.colors)
            self.board.properties(player)[property_set].append(card)

    def _collect_rent(self,
                      player,
                      card):
        """
        collect rent from other players

        Arguments:
            player {Player} -- player collecting rent
            card {rent_card} -- rent
        """
        property_set = player.choose_action(card.colors)
        rent = get_rent(property_set, self.board.properties(player)[property_set]) * self.rent_level
        if not rent:
            return

        other_players = self._other_players(player)
        collect_from = other_players if card.players == 'ALL' else [player.choose_action(other_players)]
        self._collect_money(player, rent, collect_from)

        self.deck.discard_cards([card])

    #
    # Action Options
    #
    def _do_action(self, player, card):
        # TODO: clean up ugly long if
        if card.action == 'debt collector':
            collect_from = [player.choose_action(self._other_players(player))]
            self._collect_money(player, 5000000, collect_from)
        elif card.action == 'double the rent':
            self.rent_level *= 2
        elif card.action == 'it\'s my birthday':
            collect_from = self._other_players(player)
            self._collect_money(player, 2000000, collect_from)
        elif card.action == 'pass go':
            player.draw_cards(self.deck, 2)
        elif card.action == 'deal breaker':
            self._steal_property_set(player, full_sets=True)
        elif card.action == 'sly deal':
            self._steal_property_set(player, full_sets=False)
        elif card.action == 'forced deal':
            self._steal_property_set(player, full_sets=False, swap=True)
        elif card.action in ['house', 'hotel']:
            self._lay_bonus_property(player, card)
            return

        self.deck.discard_cards([card])

    def _lay_bonus_property(self,
                            player,
                            card):
        """
        add a house or a hotel to a complete property to jack up rent

        Arguments:
            player {Player} -- player adding bonus
            card {action_card} -- hotel or house card
        """
        full_sets = [(prop_set, get_rent(prop_set, properties))
                     for prop_set, properties in self.board.properties(player).items()
                     if check_full_set(prop_set, properties) and prop_set not in ['railroad', 'utility']]
        if not full_sets:
            # cant get fancy on an incomplete property set
            return

        property_set, _ = player.choose_action(full_sets)
        self.board.properties(player)[property_set].append(card)

    def _steal_property_set(self,
                            player,
                            full_sets=False,
                            swap=False):
        """
        steal some properties from other players, because life is cruel

        Arguments:
            player {Player} -- player making the steal

        Keyword Arguments:
            full_sets {bool} -- if True, player can take full property sets from opponents (default: {False})
            swap {bool} -- if True, player must give up a property of their own in trade (default: {False})
        """
        other_players = self._other_players(player)
        sets = self.board.get_property_sets(other_players, full_sets=full_sets)
        if not sets:
            # nothing to steal
            return

        if swap:
            player_sets = self.board.get_property_sets([player], full_sets=False)
            if not player_sets:
                # no properties to trade for
                return

        victim, prop_set, properties = player.choose_action(sets)
        # give victim a chance to defend their property
        say_no_card = victim.say_no()
        if say_no_card:
            self._write_players('\r{} said no\n'.format(victim.name))
            self.deck.discard_cards([say_no_card])
            return

        self._write_players('\r{} stealing {} from {}\n'.format(player.name, str(properties), victim.name))

        # take properties from victim and give them to player
        [self._lay_property(player, prop) for prop in properties]
        self.board.reset_properties(victim, prop_set, properties)

        if swap:
            # take properties from player and give them to victim
            _, swap_set, swap_props = player.choose_action(player_sets)
            self.board.reset_properties(player, swap_set, swap_props)
            [self._lay_property(victim, prop) for prop in swap_props]
            self._write_players('\r{} giving {} to {}\n'.format(player.name, str(swap_props), victim.name))

    def _collect_money(self,
                       collector,
                       amount_owed,
                       payers):
        """
        collect money from debtors, foreclose their property too maybe

        Arguments:
            collector {Player} -- player collecting money
            amount_owed {int} -- amount of money owed
            payers {list} -- list of Players owing money
        """
        self._write_players('\r{} collecting {} from {}\n'.format(collector.name, amount_owed, str([x.name for x in payers])))

        for payer in payers:
            say_no_card = payer.say_no()
            if say_no_card:  # debt forgiveness!
                self._write_players('\r{} said no\n'.format(payer.name))
                self.deck.discard_cards([say_no_card])
                continue

            # its a cruel cruel world
            moneys, properties = self._pay(payer, amount_owed)
            [self._deposit_money(collector, money) for money in moneys]
            [self._lay_property(collector, card) for card in properties]

    #
    # Helpers
    #
    def _pay(self,
             player,
             amount):
        """
        cough up the dough to cover a debt

        Arguments:
            player {Player} -- player paying money
            amount {int} -- amount owed

        Returns:
            tuple -- ([money cards paid], [property cards paid])
        """
        # try to pay debt off using money in the bank first
        bank_payment = pay_from_bank(amount, self.board.bank(player))
        self.board.reset_bank(player, bank_payment.remaining)

        if not bank_payment.owed:
            return bank_payment.paid, []

        # foreclosure time, start taking properties if you still owe money
        # TODO: allow players to pick which properties they want to give up
        property_payment = pay_from_properties(bank_payment.owed, self.board.properties(player))

        self.board.reset_properties(player)
        [self._lay_property(player, card) for card in property_payment.remaining]

        return bank_payment.paid, property_payment.paid

    def _other_players(self,
                       player):
        """
        get the other folks in the game

        Arguments:
            player {Player} -- Player

        Returns:
            list -- list of Players
        """
        return [x for x in self.players if x != player]

    def _write_players(self,
                       message,
                       players=None,
                       board=False):
        """
        write a message to all players

        Arguments:
            message {str} -- message to send

         Keyword Arguments:
            players {list} - list of players to write to, if None sends to all (default: {None})
            board {bool} -- is message current board state (default: {False})
        """
        if not self.verbose:
            return
        players = players or self.players
        channel = 'update_board' if board else 'game_message'
        for player in players:
            player.write(message, channel)

    def _rearrange_properties(self,
                              player):
        """
        rearrange wildcard properties on a players board

        Arguments:
            player {Player} -- player rearranging
        """
        wildcard_props = self.board.get_wildcard_properties(player)
        [self._lay_property(player, prop) for prop in wildcard_props]
