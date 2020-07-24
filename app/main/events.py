from collections import defaultdict
from flask import session, request
from flask_socketio import emit, join_room, leave_room, close_room, disconnect
from .. import socketio

from game.game import MonopDealGame
from game.player import RandomPlayer, WebPlayer

GAMES = {}
ROBOTS = defaultdict(int)
PLAYERS = defaultdict(dict)
RESPONSES = defaultdict(dict)
NAMESPACE = '/game'


# TODO: utils shit
def add_player(game_id, player_id, player_name, bot=False):
    RESPONSES[game_id][player_id] = {}
    resp_dict = RESPONSES[game_id]
    if not bot:
        PLAYERS[game_id][player_id] = WebPlayer(player_name, player_id, socketio, NAMESPACE, resp_dict)
    else:
        PLAYERS[game_id][player_id] = RandomPlayer(player_name)


def get_bot_name(game_id):
    bot_number = ROBOTS[game_id]
    bot_name = 'bot {}'.format(bot_number + 1)
    ROBOTS[game_id] += 1
    return bot_name


def get_players(game_id):
    return [player.name for player in PLAYERS[game_id].values()]


@socketio.on('join_game', namespace=NAMESPACE)
def join_game(_message):
    room = session.get('room')
    player_name = session.get('player')
    player_id = request.sid

    add_player(room, player_id, player_name)
    join_room(room)

    message = '{} has entered the game.\nall participants: {}'.format(player_name, ', '.join(get_players(room)))
    emit('status', {'msg': message}, room=room)

    if len(PLAYERS[room]) >= 2:
        emit('game_ready', {'msg': ''}, room=room)


@socketio.on('add_bot', namespace=NAMESPACE)
def add_bot_player(_message):
    room = session.get('room')
    bot_name = get_bot_name(room)

    add_player(room, bot_name, bot_name, bot=True)

    message = '{} has entered the game.\nall participants: {}'.format(bot_name, ', '.join(get_players(room)))
    emit('status', {'msg': message}, room=room)

    if len(PLAYERS[room]) >= 2:
        emit('game_ready', {'msg': ''}, room=room)


@socketio.on('start', namespace=NAMESPACE)
def start_game(message):
    room = session.get('room')
    if GAMES.get(room):
        # lol concurrency bug
        emit('status', {'msg': 'game has already been started'}, room=room)
        return

    emit('game_started', {'msg': 'begin game'}, room=room)
    emit('status', {'msg': 'players: {}'.format(', '.join(get_players(room)))})

    GAMES[room] = True
    mdg = MonopDealGame(PLAYERS[room].values(), verbose=True)
    winner = mdg.play_game()

    emit('status', {'msg': '{} has won the game'.format(winner)}, room=room)

    GAMES.pop(room, None)
    emit('game_end', {'msg': True}, room=room)


@socketio.on('action', namespace=NAMESPACE)
def take_action(message):
    room = session.get('room')
    player_id = request.sid
    RESPONSES[room][player_id]['latest'] = message['msg']
    # NOTE: have to sleep here for a second so that the player object can read the message
    socketio.sleep()


@socketio.on('text', namespace=NAMESPACE)
def send_chat_message(message):
    room = session.get('room')
    player = session.get('player')
    emit('chat_message', {'msg': '<{}>: {}'.format(player, message['msg'])}, room=room)


@socketio.on('disconnect',  namespace=NAMESPACE)
def disconnect_client():
    room = session.get('room')
    player_id = request.sid
    player = session.get('player')
    PLAYERS[room].pop(player_id, None)
    GAMES.pop(room, None)

    if len(PLAYERS[room]) >= 1:
        emit('status', {'msg': '{} has exited.\ngame over'.format(player)}, room=room)
        enough_players = len(PLAYERS[room]) >= 2
        emit('game_end', {'msg': enough_players}, room=room)
    else:
        ROBOTS.pop(room, None)
        close_room(room)
        disconnect()
