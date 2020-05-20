from flask_wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required


class GameForm(Form):
    player = StringField('Name', validators=[Required()])
    room = StringField('Game ID', validators=[Required()])
    submit = SubmitField('Enter Game')
