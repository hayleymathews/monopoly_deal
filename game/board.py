
from collections import defaultdict
from .utils import check_full_set


class Board(object):
    def __init__(self, players):
        self.players = players
        self._banks = {player.name: [] for player in self.players}
        self._properties = {player.name: defaultdict(list) for player in self.players}

    def __repr__(self):
        # TODO: better here
        for player in self.players:
            print(player.name)
            print('bank:')
            for mc in self._bank[player.name]:
                print('  ' + str(mc))
            print('properties:')
            for color, props in self._properties[player.name].items():
                print('  ' + color)
                if check_full_set(color, props):
                    print('  ' + '************')
                for prop in props:
                    print('    ' + str(prop))
            print()

    def properties(self, player):
        return self._properties[player.name]

    def reset_properties(self, player, property_set=None, properties=None):
        if not property_set:
            self._properties[player.name] = defaultdict(list)
        else:
            [self._properties[player.name][property_set].remove(prop) for prop in properties]

    def bank(self, player):
        return self._banks[player.name]

    def reset_bank(self, player, money):
        self._banks[player.name] = money
