from game.game import MonopDealGame
from game.player import RandomPlayer, TerminalPlayer

if __name__ == "__main__":
    player_name = input('enter your name: ')
    num_players = int(input('enter number of players: '))

    term_player = TerminalPlayer(player_name)
    bots = [RandomPlayer('bot {}'.format(n + 1)) for n in range(num_players)]
    mdg = MonopDealGame(bots + [term_player], verbose=True)
    mdg.play_game()
