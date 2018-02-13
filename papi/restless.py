import flask_restless
from models import Deck, Card, Balance, db


restless = flask_restless.APIManager(flask_sqlalchemy_db=db)
for model in [Deck, Card, Balance]:
    restless.create_api(model,
            url_prefix='/restless/v1',
            methods=['GET'])

def init_restless(app):
    restless.init_app(app)
