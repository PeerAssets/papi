from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Deck(db.Model):
    """"""
    __tablename__ = "decks"
    id = db.Column(db.String, primary_key=True, unique=True)
    name = db.Column(db.String)
    issuer = db.Column(db.String)
    issue_mode = db.Column(db.Integer)
    decimals = db.Column(db.Integer)
    subscribed = db.Column(db.Boolean)
    
    #----------------------------------------------------------------------
    def __init__(self, id, name, issuer, issue_mode, decimals, subscribed):
        """"""
        self.id = id
        self.name = name
        self.issuer = issuer
        self.issue_mode = issue_mode
        self.decimals = decimals
        self.subscribed = subscribed

class Card(db.Model):
    """"""
    __tablename__ = "cards"
    id = db.Column(db.String, primary_key=True, unique=True) #concatenate txid + blockseq + cardseq
    txid = db.Column(db.String)
    cardseq = db.Column(db.Integer)
    receiver = db.Column(db.String)
    sender = db.Column(db.String)
    amount = db.Column(db.Integer)
    ctype = db.Column(db.String)
    blocknum = db.Column(db.Integer)
    blockseq = db.Column(db.Integer)
    deck_id = db.Column(db.String)
    
    #----------------------------------------------------------------------
    def __init__(self, id, txid, cardseq, receiver, sender, amount, ctype, blocknum, blockseq, deck_id):
        """"""
        self.id = id
        self.txid = txid
        self.cardseq = cardseq
        self.receiver = receiver
        self.sender = sender
        self.amount = amount
        self.ctype = ctype
        self.blocknum = blocknum
        self.blockseq = blockseq
        self.deck_id = deck_id

class Balance(db.Model):
    """"""
    __tablename__ = 'balances' 
    id = db.Column(db.Integer,primary_key=True, unique=True)
    account = db.Column(db.String)
    value = db.Column(db.Integer)
    short_id = db.Column(db.String)

    #----------------------------------------------------------------------
    def __init__(self, account, value, short_id):
        """"""
        self.account = account
        self.value = value
        self.short_id = short_id


def init_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()
