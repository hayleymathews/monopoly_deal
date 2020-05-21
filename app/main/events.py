from collections import defaultdict
from flask import session, request
from flask_socketio import emit, join_room, leave_room, close_room
from .. import socketio

from game.game import MonopDealGame
from game.player import RandomPlayer, WebPlayer

ROBOTS = defaultdict(int)
PLAYERS = defaultdict(dict)
RESPONSES = defaultdict(dict)


# TODO: utils shit
def add_player(game_id, player_id, player_name, bot=False):
    RESPONSES[game_id][player_id] = {}
    resp_dict = RESPONSES[game_id]
    if not bot:
        PLAYERS[game_id][player_id] = WebPlayer(player_name, player_id, socketio, resp_dict)
    else:
        PLAYERS[game_id][player_id] = RandomPlayer(player_name)


def get_bot_name(game_id):
    bot_number = ROBOTS[game_id]
    bot_name = 'bot {}'.format(bot_number)
    ROBOTS[game_id] += 1
    return bot_name


@socketio.on('joined', namespace='/game')
def joined(message):
    room = session.get('room')
    player = session.get('player')
    player_id = request.sid
    add_player(room, player_id, player)
    join_room(room)
    emit('status', {'msg': session.get('player') + ' has entered the room.'}, room=room)


@socketio.on('add_bot', namespace='/game')
def add_bot_player(message):
    room = session.get('room')
    bot_name = get_bot_name(room)
    add_player(room, 'x', bot_name, bot=True)
    emit('status', {'msg': '{} has entered the room.'.format(bot_name)}, room=room)


@socketio.on('start', namespace='/game')
def start_game(message):
    room = session.get('room')
    emit('status', {'msg': 'begin game'}, room=room)

    mdg = MonopDealGame(PLAYERS[room].values(), verbose=True)
    winner = mdg.play_game()

    emit('status', {'msg': '{} has won the game'.format(winner)}, room=room)

    close_room(room)


@socketio.on('action', namespace='/game')
def action(message):
    room = session.get('room')
    player_id = request.sid
    RESPONSES[room][player_id]['latest'] = message['msg']


@socketio.on('text', namespace='/game')
def text(message):
    room = session.get('room')
    player = session.get('player')
    emit('chat_message', {'msg': player + ':' + message['msg']}, room=room)
