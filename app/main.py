import pypeerassets as pa
from binascii import hexlify, unhexlify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Card, Deck, Balance
from utils.state import init_state
from utils.sync import Sync
from conf import *
import sys

connection = Sync().connect()
node = connection.node

engine = create_engine(db_engine)
Session = sessionmaker(bind=engine)
session = Session()

def init_p2thkeys():

    if autoload:
        pa.pautils.load_p2th_privkey_into_local_node(node, production)

def load_key(deck):
    try:
        wif = pa.Kutil(privkey=unhexlify(deck.id), network=node.network).wif
        node.importprivkey( wif, deck.id)
        sys.stdout.write('\rImported {}'.format(wif))
        sys.stdout.flush()
    except:
        pass
    

def commit():
    try:
        session.commit()
    except:
        session.rollback()  


def add_deck(deck):
    if deck is not None:
        try:
            entry = session.query(Deck).filter(Deck.id == deck.id).first()
        except:
            entry = None

        subscribe = any(deck_id in subscribed for deck_id in ('*', deck.id))

        if entry is None:
            try:
                data = hexlify(deck.asset_specific_data).decode()
                D = Deck( deck.id, deck.name, deck.issuer, deck.issue_mode, deck.number_of_decimals, subscribe, data)
                session.add(D)
            except Exception as e:
                pass
        else:
            session.query(Deck).filter(Deck.id == deck.id).update({"subscribed": subscribe})

        commit()


def add_cards(deck):

    def message(n):
        sys.stdout.write('\r{} Card(s) for Deck {} '.format(n, deck.id))
        sys.stdout.flush()

    for n, card in enumerate(pa.find_all_valid_cards(node, deck)):

        try:
            entry = session.query(Card).filter(Card.txid == card.txid).filter(Card.blockseq == card.blockseq).filter(Card.cardseq == card.cardseq).first()
        except (Exception,TypeError) as e:
            if isinstance(e, TypeError):
                continue
            entry = None
        
        if entry is None:
            data = hexlify(card.asset_specific_data).decode()
            C = Card( card.txid, card.blockhash, card.cardseq, card.receiver[0], card.sender, 
            card.amount[0], card.type, card.blocknum, card.blockseq, card.deck_id, False, data )
            session.add(C)
    commit()
    #message(n)
            

def update_decks(txid):
    try:
        deck = pa.find_deck(node, txid, version)
        add_deck(deck) 
    except KeyError:
        ''' Transaction most likely still in mempool '''
        pass


def which_deck(txid):
    deck = node.gettransaction(txid)
    deck_id = None

    if 'details' in deck.keys():
         owneraccounts = [details['account'] for details in deck['details'] if details['account']]
         if owneraccounts:
             deck_id = [details['account'] for details in deck['details'] if details['account']][0]

    if deck_id is not None:
        if deck_id in ('PAPROD','PATEST'):
            update_decks(txid)

        elif any(i in subscribed for i in ('*', deck_id)):
            deck = pa.find_deck(node, deck_id, version)

            if not checkpoint(deck):
                remove_no_confirms(deck_id)
                add_cards( deck )
                init_state(deck.id)

        return {'walletnotify': True, 'deck_id':deck_id}
    else:
        return {'walletnotify': False, 'deck_id': deck_id}

def validate(deck):

    validate = node.validateaddress(deck.p2th_address)

    if validate['isvalid']:
        
        if not validate['ismine']:
            load_key(deck)
            
            if 'account' in validate and validate['account'] != deck.id:
                node.move(deck.p2th_address, deck.id)
    

def checkpoint(deck):
    ''' check if deck_id is loaded into the node'''
    validate(deck)

    ''' list all transactions for a particular deck '''
    txs = node.listtransactions(deck.id)
    ''' get deck object of current deck.id '''
    try:
        deck = pa.find_deck(node, deck.id, version)
    except KeyError:
        return True


    if isinstance(txs,list):
        ''' Make sure txs is a list rather than a dict with an error. Reverse list order.'''
        checkpoint = txs[::-1]
        ''' Get the most recent card transaction recorded in the database for the given deck '''
        try:
            _checkpoint = session.query(Card).filter(Card.deck_id == deck.id).order_by(Card.blocknum.desc()).first()
        except:
           _checkpoint = None

        if _checkpoint is not None and _checkpoint.blockhash:
            ''' If database query doesn't return None type then checkpoint exists'''
            for i, v in enumerate(checkpoint):
                ''' for each transaction in local node listtransactions '''
                if ('txid','blockhash') in v.keys():
                    ''' Check that keys exists within dict ''' 
                    if v['blockhash'] == _checkpoint.blockhash:
                        return True
                    else:
                        txid = v['txid']
                        rawtx = node.getrawtransaction(txid,1)

                        try:
                            ''' check if it's a valid PeerAssets transaction '''
                            pa.pautils.validate_card_transfer_p2th(deck, rawtx)
                            ''' return False if checkpoints don't match and True if they do '''

                            return _checkpoint.blockhash == v['blockhash']
                        except:
                            continue

            return False

def remove_no_confirms(deck_id):
    try:
        tx = session.query(Card).filter(Card.blockhash == "").filter(Card.blocknum == 0).filter(Card.deck_id == deck_id)
    except:
        tx = None

    if tx is None:
        pass
    else:
        tx.delete()
        commit()