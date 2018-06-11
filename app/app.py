from flask import Flask
from conf import *
from routes import *
from utils.restless import init_restless

__version__ = "0.1"


def create_app(config=None, app_name=None):

    app = Flask(__name__)
    ''' Setup'''
    app.config['SQLALCHEMY_DATABASE_URI'] = db_engine
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    configure_extensions(app)
    configure_blueprints(app)
    return app


def configure_extensions(app):
    from flask_cors import CORS

    CORS(app)
    init_restless(app)
    init_db(app)


def configure_blueprints(app):
    app.register_blueprint(api)


app = create_app()
