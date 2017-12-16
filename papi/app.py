from flask import Flask, jsonify, redirect, url_for, request
from sqlalchemy.sql.functions import func
from conf import db_engine
from data import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_engine
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

    if deck_id is not None:
        deck = db.session.query(Deck).filter(Deck.id == deck_id).first()
        if deck:
            deck = deck.__dict__
            del deck['_sa_instance_state']
            deck['cards'] = get_cards(deck_id)
            return jsonify(deck)
    else:
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

@app.route('/api/v1/decks/<deck_id>/balances', methods=['GET','POST'])
def balances(deck_id):
    short_id = deck_id[0:10]
    balances = {}
    Balances = db.session.query(Balance).filter( Balance.short_id == short_id  )

    if request.method == 'POST':
        Balances = Balances.filter( Balance.account == request.args.get('address') )
    else:
        Balances = Balances.filter( func.char_length( Balance.account ) == 34 )

    for balance in Balances:
        balance = balance.__dict__
        balances[balance["account"]] =  balance["value"]

    return jsonify( balances )

@app.route('/api/v1/decks/<deck_id>/total', methods=['GET'])
def total(deck_id):

    issuer = db.session.query(Deck).filter(Deck.id == deck_id).first().issuer
    short_id = deck_id[0:10]
    balances = []
    Balances = db.session.query(Balance).filter( Balance.short_id == short_id  )
    Issued = Balances.filter( Balance.account.contains(issuer)).filter(func.char_length( Balance.account ) > 34)
    Accounts = Balances.filter( func.char_length( Balance.account ) == 34)

    issued = abs( Issued.with_entities(func.sum(Balance.value)).scalar() )
    total = Accounts.with_entities(func.sum(Balance.value)).scalar()

    if issued == total:
        return jsonify( {'supply': issued} )

@app.route('/alert', methods=['POST'])
def alert():
    txid = request.values.get('txid')
    blockhash = request.values.get('blockhash')
    if txid is not None:
        deck = which_deck(txid)
        if deck in subscribed:
            DeckState(deck)
    if blockhash is not None:
        init_decks()
    return jsonify({'walletnotify': bool(txid), 'blocknotify': bool(blockhash)})

if __name__ == '__main__':
    init_db()
    init_pa()
    app.run(host='0.0.0.0',port=5555)
