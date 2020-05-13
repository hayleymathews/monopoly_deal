import telnetlib3
import asyncio
import nest_asyncio

from game.game import MonopDealGame
from game.player import RandomPlayer, TelNetPlayer

nest_asyncio.apply()

players = []
bot_players = []
joined = []


@asyncio.coroutine
def shell(reader, writer):
    writer.write('enter your name: ')
    inp = yield from reader.read(10)
    players.append(TelNetPlayer(inp, writer, reader))

    writer.write('enter number of bot players: ')
    inp = yield from reader.read(10)
    try:
        num_bots = int(inp)
    except:
        num_bots = 0
    bot_players.extend([RandomPlayer('bot {}'.format(n + 1)) for n in range(num_bots)])

    writer.write('ready? ')
    inp = yield from reader.read(10)
    joined.append(inp)

    if len(joined) == len(players):
        writer.write(str(players))
        mdg = MonopDealGame(players + bot_players, verbose=True)
        mdg.play_game()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    coro = telnetlib3.create_server(port=6023, shell=shell)
    server = loop.run_until_complete(coro)
    loop.run_until_complete(server.wait_closed())
