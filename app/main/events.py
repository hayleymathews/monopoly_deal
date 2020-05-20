from collections import defaultdict
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from .. import socketio

from game.game import MonopDealGame
from game.player import RandomPlayer, WebPlayer

GAMES = {}
PLAYERS = defaultdict(dict)
RESPONSES = defaultdict(dict)


def add_player(game_id, player_id, player_name, bot=False):
    RESPONSES[game_id][player_id] = {}
    resp_dict = RESPONSES[game_id]
    if not bot:
        PLAYERS[game_id][player_id] = WebPlayer(player_name, player_id, socketio, resp_dict)
    else:
        PLAYERS[game_id][player_id] = RandomPlayer(player_name)


@socketio.on('joined', namespace='/game')
def joined(message):
    room = session.get('room')
    player = session.get('player')
    player_id = request.sid
    add_player(room, player_id, player)

    join_room(room)
    emit('status', {'msg': session.get('player') + ' has entered the room.'}, room=room)


@socketio.on('ready', namespace='/game')
def player_ready(message):
    room = session.get('room')
    print('TITS' * 100)
    print(id(socketio),  request.sid)

    print(PLAYERS[room])

    emit('status', {'msg': 'begin game'}, room=room)

    mdg = MonopDealGame(PLAYERS[room].values(), verbose=True)
    GAMES[room] = mdg

    winner = mdg.play_game()
    print('&' * 100)
    import time
    time.sleep(5)
    print('*' * 100)
    time.sleep(5)

    emit('status', {'msg': '{} has won the game'.format(winner)}, room=room)


@socketio.on('add_bot', namespace='/game')
def add_bot_player(message):
    room = session.get('room')
    add_player(room, 'x', 'roboto', bot=True)
    emit('status', {'msg': 'roboto has entered the room.'}, room=room)


@socketio.on('text', namespace='/game')
def text(message):
    room = session.get('room')
    player = session.get('player')

    emit('chat_message', {'msg': player + ':' + message['msg']}, room=room)


@socketio.on('action', namespace='/game')
def action(message):
    room = session.get('room')
    player_id = request.sid
    player = PLAYERS[room][player_id]
    print(player)
    print(id(player))
    print(room)
    print(message)

    RESPONSES[room][player_id]['latest'] = message['msg']

