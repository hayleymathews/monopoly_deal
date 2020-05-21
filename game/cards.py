from collections import namedtuple

END_TURN = 'end turn'
SHOW_BOARD = 'show board'
REARRANGE_PROPS = 'rearrange properties'

BROWN = 'brown'
DARK_BLUE = 'dark blue'
GREEN = 'green'
LIGHT_BLUE = 'light blue'
ORANGE = 'orange'
PURPLE = 'purple'
RAILROAD = 'railroad'
RED = 'red'
UTILITY = 'utility'
YELLOW = 'yellow'
WILD_CARD = 'Wild Card'

COLORS = [BROWN,
          DARK_BLUE,
          GREEN,
          LIGHT_BLUE,
          ORANGE,
          PURPLE,
          RAILROAD,
          RED,
          UTILITY,
          YELLOW]

RENTS = {BROWN: [1000000, 2000000],
         DARK_BLUE: [3000000, 8000000],
         GREEN: [2000000, 4000000, 7000000],
         LIGHT_BLUE: [1000000, 2000000, 3000000],
         ORANGE: [1000000, 3000000, 5000000],
         PURPLE: [1000000, 2000000, 4000000],
         RAILROAD: [1000000, 2000000, 3000000, 4000000],
         RED: [2000000, 3000000, 6000000],
         UTILITY: [1000000, 2000000],
         YELLOW: [2000000, 4000000, 6000000]
         }

money_card = namedtuple('money', ['value'])
MONEY_COUNTS = [(10000000, 1),
                (5000000, 2),
                (4000000, 3),
                (3000000, 3),
                (2000000, 5),
                (1000000, 6)]
MONEY_CARDS = [money_card(val) for val, count in MONEY_COUNTS for _ in range(count)]


rent_card = namedtuple('rent', ['colors', 'players'])
RENT_COUNTS = [(COLORS, 1, 3),
               ([PURPLE, ORANGE], 'ALL', 2),
               ([RAILROAD, UTILITY], 'ALL', 2),
               ([GREEN, DARK_BLUE], 'ALL', 2),
               ([BROWN, LIGHT_BLUE], 'ALL', 2),
               ([RED, YELLOW], 'ALL', 2)]
RENT_CARDS = [rent_card(colors, players) for colors, players, count in RENT_COUNTS for _ in range(count)]


action_card = namedtuple('action', ['action', 'value'])
ACTION_COUNTS = [('deal breaker', 5000000, 2),
                 ('debt collector', 3000000, 3),
                 ('double the rent', 1000000, 2),
                 ('forced deal', 3000000, 3),
                 ('hotel', 4000000, 3),
                 ('house', 3000000, 2),
                 ('it\'s my birthday', 2000000, 3),
                 ('just say no', 4000000, 3),
                 ('pass go', 1000000, 10),
                 ('sly deal', 3000000, 3)]
ACTION_CARDS = [action_card(action, value) for action, value, count in ACTION_COUNTS for _ in range(count)]

property_card = namedtuple('property', ['colors', 'name', 'value'])
PROPERTY_CARDS = [
    property_card([BROWN], 'Baltic Avenue', 1000000),
    property_card([BROWN], 'Mediterannean Avenue', 1000000),
    property_card([DARK_BLUE], 'Boardwalk', 4000000),
    property_card([DARK_BLUE], 'Park Place', 4000000),
    property_card([GREEN], 'North Carlonia Avenue', 4000000),
    property_card([GREEN], 'Pacific Avenue', 4000000),
    property_card([GREEN], 'Pennsylvania Avenue', 4000000),
    property_card([LIGHT_BLUE], 'Connecticut Avenue', 1000000),
    property_card([LIGHT_BLUE], 'Oriental Avenue', 1000000),
    property_card([LIGHT_BLUE], 'Vermont Avenue', 1000000),
    property_card([ORANGE], 'New York Avenue', 2000000),
    property_card([ORANGE], 'St James Place', 2000000),
    property_card([ORANGE], 'Tennessee Avenue', 2000000),
    property_card([PURPLE], 'St Charles Place', 2000000),
    property_card([PURPLE], 'Virginia Avenue', 2000000),
    property_card([PURPLE], 'States Avenue', 2000000),
    property_card([RAILROAD], 'Short Line', 2000000),
    property_card([RAILROAD], 'B&O Railroad', 2000000),
    property_card([RAILROAD], 'Reading Railroad', 2000000),
    property_card([RAILROAD], 'Pennsylvania Railroad', 2000000),
    property_card([RED], 'Kentucky Avenue', 3000000),
    property_card([RED], 'Indiana Avenue', 3000000),
    property_card([RED], 'Illinois Avenue', 3000000),
    property_card([UTILITY], 'Water Works', 2000000),
    property_card([UTILITY], 'Electric Company', 2000000),
    property_card([YELLOW], 'Ventnor Avenue', 3000000),
    property_card([YELLOW], 'Marvin Gardens', 3000000),
    property_card([YELLOW], 'Atlantic Avenue', 3000000),
    property_card([DARK_BLUE, GREEN], WILD_CARD, 4000000),
    property_card([LIGHT_BLUE, BROWN], WILD_CARD, 1000000),
    property_card(COLORS, WILD_CARD, 0),
    property_card(COLORS, WILD_CARD, 0),
    property_card([ORANGE, PURPLE], WILD_CARD, 2000000),
    property_card([ORANGE, PURPLE], WILD_CARD, 2000000),
    property_card([GREEN, RAILROAD], WILD_CARD, 4000000),
    property_card([LIGHT_BLUE, RAILROAD], WILD_CARD, 4000000),
    property_card([UTILITY, RAILROAD], WILD_CARD, 2000000),
    property_card([YELLOW, RED], WILD_CARD, 3000000),
    property_card([YELLOW, RED], WILD_CARD, 3000000),
]

CARDS = MONEY_CARDS + RENT_CARDS + ACTION_CARDS + PROPERTY_CARDS
