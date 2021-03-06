from flask import Flask
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap

socketio = SocketIO()


def create_app(debug=True):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjndDWD344_!67#'
    bootstrap = Bootstrap(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, async_mode="eventlet")
    return app
