from flask import Flask, jsonify, redirect, url_for
from data import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///papi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('decks'))

@app.route('/api/v1/decks/<deck_id>', methods=['GET'])
@app.route('/api/v1/decks', methods=['GET'], defaults={'deck_id':None}, strict_slashes=False)
def decks(deck_id):
    deck = None

    def get_cards(deck_id):
        cards = []
        Cards = db.session.query(Card).filter(Card.deck_id == deck_id).order_by(Card.blocknum,Card.blockseq,Card.cardseq).all()
        for card in Cards:
            card = card.__dict__
            del card['_sa_instance_state']
            cards.append(card)
        return cards

    if deck_id is not None and germ_free(deck_id, 'hex'):
        deck = db.session.query(Deck).filter(Deck.id == deck_id).first()
        if deck:
            deck = deck.__dict__
            del deck['_sa_instance_state']
            deck['cards'] = get_cards(deck_id)
        else:
            deck = {'id': 'Error: deck_id does not exist'}
        return jsonify(deck)

    elif deck_id is None and germ_free(deck_id, 'hex'):
        decks = []
        if not autoload:
            Decks = db.session.query(Deck).filter(Deck.id.in_(subscribed)).all()
        else:
            Decks = db.session.query(Deck).all()
        
        for deck in Decks:
            deck = deck.__dict__
            del deck['_sa_instance_state']
            decks.append(deck)

        return jsonify(decks)

    else:
        invalid = {'id': 'Error: not a valid deck_id'}
        return jsonify( invalid )

@app.route('/api/v1/decks/<deck_id>/balances', methods=['GET'])
def balances(deck_id):

    if germ_free(deck_id, 'hex'): 
        balances = []
        Balances = db.session.query(Balance).filter_by(short_id = deck_id[0:10]).all()

        for balance in Balances:
            balance = balance.__dict__
            del balance['_sa_instance_state']
            balances.append(balance)
            print(balance)

        else:
            balances = {'id': 'Error: deck_id does not exist'}
    else:
        balances = {'id': 'Error: not a valid deck_id'}

    return jsonify( balances )

if __name__ == '__main__':
    init_db()
    init_pa()
    app.run(host='0.0.0.0',port=5555)
