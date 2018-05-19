from flask import Flask, jsonify, redirect, url_for, request
from flask_cors import CORS
from sqlalchemy.sql.functions import func
from conf import db_engine
from data import *
from models import db, init_db
from restless  import init_restless
import pypeerassets as pa

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = db_engine
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def index():
    return redirect(url_for('decks'))

@app.route('/api/v1/decks/<deck_id>', methods=['GET'])
@app.route('/api/v1/decks', methods=['GET'], defaults={'deck_id':None}, strict_slashes=False)
def decks(deck_id):
    deck = None

    def get_cards(deck_id):
        cards = []
        Cards = db.session.query(Card).filter(Card.deck_id == deck_id)
        
        if request.values.get('address'):
            address = request.values.get('address')
            Cards = Cards.filter( (Card.receiver == address) | (Card.sender == address) )
        
        if request.values.get('valid'):
            valid = request.values.get('valid')
            Cards = Cards.filter( Card.valid == valid )

        Cards = Cards.order_by(Card.blocknum,Card.blockseq,Card.cardseq).all()

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

@app.route('/api/v1/decks/<deck_id>/balances', methods=['GET','POST'], strict_slashes=False)
def balances(deck_id):
    short_id = deck_id[0:10]
    balances = {}
    Balances = db.session.query(Balance).filter( Balance.short_id == short_id  )

    if request.args.get('address'):
        Balances = Balances.filter( Balance.account == request.args.get('address') )
    else:
        Balances = Balances.filter( func.char_length( Balance.account ) == 34 )

    for balance in Balances:
        balance = balance.__dict__
        balances[balance["account"]] =  balance["value"]

    #Check if balances was returned null
    if balances:
        return jsonify( balances )
    else:
        return jsonify( 'no balances found for this deck' )

@app.route('/api/v1/decks/<deck_id>/total', methods=['GET'], strict_slashes=False)
def total(deck_id):

    issuer = db.session.query(Deck).filter(Deck.id == deck_id).first().issuer
    short_id = deck_id[0:10]
    balances = []
    Balances = db.session.query(Balance).filter( Balance.short_id == short_id  )
    Issued = Balances.filter( Balance.account.contains(issuer)).filter(func.char_length( Balance.account ) > 34)
    Accounts = Balances.filter( func.char_length( Balance.account ) == 34)

    #Calling abs() on this function produces a "Bad operand type for abs(): NoneType error"
    #issued = abs( Issued.with_entities(func.sum(Balance.value)).scalar() )
    #Do a check for when supply is returned null
    #If supply is not null, return abs(issued)
    issued = Issued.with_entities(func.sum(Balance.value)).scalar()
    
    total = Accounts.with_entities(func.sum(Balance.value)).scalar()

    if ( issued ):
        if (abs(issued) == total):
            return jsonify( {'supply': abs(issued)} )
        else:
            return jsonify( {'Error:': 'Invalid card transfers found in database', 'Total issued:': abs(issued), 'Total valid:': total} )
    else:
        return jsonify({'Error:': 'No cards found for this deck.'}) 



@app.route('/alert', methods=['POST'])
def alert():
    txid = request.values.get('txid')
    if txid is not None:
        deck = which_deck(txid)
        if deck is not None and deck['deck_id'] in subscribed:
            update_state(deck)

    return jsonify({'walletnotify': bool(txid)})

if __name__ == '__main__':
    init_db(app)
    init_restless(app)
    init_pa()
    app.run(host='0.0.0.0',port=5555)
