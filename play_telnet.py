import socket
import asyncio
import nest_asyncio
import telnetlib3
from telnetlib3 import ECHO, SGA, WONT

from game.game import MonopDealGame
from game.player import RandomPlayer, TelNetPlayer

nest_asyncio.apply()

# some sloppy shit to be global
players = []
joined = []
bot_players = []
num_bots = 0


@asyncio.coroutine
def shell(reader, writer):   
    writer.iac(WONT, ECHO)
    writer.iac(WONT, SGA)
    writer.write('enter your name: \r\n')
    inp = yield from reader.readline()
    players.append(TelNetPlayer(inp.rstrip(), writer, reader))

    if len(players) == 1:
        writer.write('\renter number of bot players: \r\n')
        inp = yield from reader.readline()
        try:
            num_bots = int(inp.rstrip())
        except:
            num_bots = 0
        bot_players.extend([RandomPlayer('bot {}'.format(n + 1)) for n in range(num_bots)])

    writer.write('\rready? \r\n')
    inp = yield from reader.read(10)
    joined.append(inp)

    if len(joined) == len(players):
        mdg = MonopDealGame(players + bot_players[:num_bots], verbose=True)
        mdg.play_game()


if __name__ == '__main__':
    kwargs = telnetlib3.parse_server_args()
    kwargs['shell'] = shell
    kwargs['host'] = socket.gethostbyname(socket.gethostname())
    kwargs['port'] = 11111
    print(kwargs)
    telnetlib3.run_server(**kwargs)
