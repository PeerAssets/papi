from flask import Flask
from conf import *
from routes import *
from models import *
from utils.extensions import rq
from utils.restless import init_restless
from utils.sync import Sync

def create_app(config=None, app_name=None):

    app = Flask(__name__)
    ''' Setup'''
    app.config['SQLALCHEMY_DATABASE_URI'] = db_engine
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['RQ_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['RQ_ASYNC'] = True
    configure_extensions(app)
    configure_blueprints(app)
    return app


def configure_extensions(app):
    from flask_cors import CORS

    CORS(app)
    rq.init_app(app)
    init_restless(app)
    init_db(app)

def configure_blueprints(app):
    app.register_blueprint(api)

app = create_app()
