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
    asset_specific_data = db.Column(db.String)
    
    #----------------------------------------------------------------------
    def __init__(self, id, name, issuer, issue_mode, decimals, subscribed, asset_specific_data):
        """"""
        self.id = id
        self.name = name
        self.issuer = issuer
        self.issue_mode = issue_mode
        self.decimals = decimals
        self.subscribed = subscribed
        self.asset_specific_data = asset_specific_data

class Card(db.Model):
    """"""
    __tablename__ = "cards"
    txid = db.Column(db.String, primary_key=True)
    blockhash = db.Column(db.String)
    cardseq = db.Column(db.Integer, primary_key=True)
    receiver = db.Column(db.String)
    sender = db.Column(db.String)
    amount = db.Column(db.BigInteger)
    ctype = db.Column(db.String)
    blocknum = db.Column(db.Integer)
    blockseq = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.String)
    valid = db.Column(db.Boolean)
    asset_specific_data = db.Column(db.String)
    __table_args__ = (db.UniqueConstraint('txid','blockseq','cardseq'),)
    
    #----------------------------------------------------------------------
    def __init__(self, txid, blockhash, cardseq, receiver, sender, amount, ctype, blocknum, blockseq, deck_id, valid, asset_specific_data):
        """"""
        self.txid = txid
        self.blockhash = blockhash
        self.cardseq = cardseq
        self.receiver = receiver
        self.sender = sender
        self.amount = amount
        self.ctype = ctype
        self.blocknum = blocknum
        self.blockseq = blockseq
        self.deck_id = deck_id
        self.valid = valid
        self.asset_specific_data = asset_specific_data

class Balance(db.Model):
    """"""
    __tablename__ = 'balances' 
    id = db.Column(db.Integer,primary_key=True, unique=True)
    account = db.Column(db.String)
    value = db.Column(db.BigInteger)
    short_id = db.Column(db.String)
    checkpoint = db.Column(db.String)
    #----------------------------------------------------------------------
    def __init__(self, account, value, short_id, checkpoint):
        """"""
        self.account = account
        self.value = value
        self.short_id = short_id
        self.checkpoint = checkpoint

def init_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()