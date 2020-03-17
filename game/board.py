
from collections import defaultdict
from utils import check_full_set, get_rent
from cards import RENTS


class Board(object):
    def __init__(self, players):
        self.players = players
        self._banks = {player.name: [] for player in self.players}
        self._properties = {player.name: defaultdict(list) for player in self.players}

    def show_board(self):
        # TODO: better here
        for player in self.players:
            print(player.name)
            print('BANK value: $' + str(sum(x.value for x in self._banks[player.name])))
            for mc in self._banks[player.name]:
                print('  ' + str(mc))
            print('PROPERTIES count: ' + str(sum(1 for props in self._properties[player.name].values() for prop in props)))
            for color, props in self._properties[player.name].items():
                print('  ' + color + '    rent: $' + str(get_rent(color, props)) + '    ' + str(len(props)) + '/' + str(len(RENTS[color])))
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
            self._properties[player.name][property_set] = [x for x in self._properties[player.name][property_set] if x not in properties]

    def bank(self, player):
        return self._banks[player.name]

    def reset_bank(self, player, money):
        self._banks[player.name] = money

    def get_property_sets(self,
                          players,
                          full_sets=False):
        """
        get property sets from players

        Arguments:
            players {list} -- list of Players to get property

        Keyword Arguments:
            full_sets {bool} -- include full sets (default: {False})

        Returns:
            list -- [(player, property set, [properties])]
        """
        if full_sets:
            return [(player, prop_set, properties) for player in players
                    for prop_set, properties in self.properties(player).items()
                    if check_full_set(prop_set, properties)]
        return [(player, prop_set, [prop]) for player in players
                for prop_set, properties in self.properties(player).items()
                if not check_full_set(prop_set, properties)
                for prop in properties]
