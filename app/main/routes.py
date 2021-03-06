import uuid
from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import GameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = GameForm()
    if form.validate_on_submit():
        session['player'] = form.player.data
        session['room'] = form.room.data if form.join.data else str(uuid.uuid4())
        session['chat_room'] = form.room.data + '_chat'
        return redirect(url_for('.game'))
    elif request.method == 'GET':
        form.player.data = session.get('player', '')
        form.room.data = session.get('room', '')
    return render_template('index.html', form=form)


@main.route('/game')
def game():
    player = session.get('player', '')
    room = session.get('room', '')
    if player == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('game.html', name=player, room=room)
