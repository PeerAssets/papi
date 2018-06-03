import pypeerassets as pa
from binascii import hexlify
from models import Deck, Card, Balance, db
from .sync import node
from .state import DeckState, init_state
from sqlalchemy.exc import IntegrityError
from conf import *
import sys


def init_p2thkeys():

    if autoload:
        pa.pautils.load_p2th_privkey_into_local_node(node, production)


def commit():
    try:
        db.session.commit()
    except:
        db.session.rollback()


def add_deck(deck):
    if deck is not None:
        try:
            entry = db.session.query(Deck).filter(Deck.id == deck.id).first()
        except:
            entry = None
        if '*' in subscribed:
            subscribe = True
        else:
            subscribe = deck.id in subscribed

        if not entry:
            try:
                data = hexlify(deck.asset_specific_data).decode()
                D = Deck( deck.id, deck.name, deck.issuer, deck.issue_mode, deck.number_of_decimals, subscribe, data)
                db.session.add(D)
                commit()
            except Exception as e:
                print(e)
                pass
        else:
            db.session.query(Deck).filter(Deck.id == deck.id).update({"subscribed": subscribe})
            commit()


def add_cards(cards):
    if cards is not None:
        for card in cards:
            try:
                entry = db.session.query(Card).filter(Card.txid == card.txid).filter(Card.blockseq == card.blockseq).filter(Card.cardseq == card.cardseq).first()
            except:
                entry = None
            
            if not entry:
                data = hexlify(card.asset_specific_data).decode()
                C = Card( card.txid, card.blockhash, card.cardseq, card.receiver[0], card.sender, 
                card.amount[0], card.type, card.blocknum, card.blockseq, card.deck_id, False, data )
                db.session.add(C)
            commit()


def load_key(deck_id):
    from binascii import unhexlify
    try:
        wif = pa.Kutil(privkey=unhexlify(deck_id), network=node.network).wif
        node.importprivkey( wif, deck_id)
    except Exception as e:
        print(e)


def init_decks():
    accounts = node.listaccounts()

    def message(n):
        sys.stdout.write('\r{} Decks Loaded\r'.format(n))
        sys.stdout.flush()

    if not autoload:
        decks = [pa.find_deck(node,txid,version) for txid in subscribed]
    else:
        decks = pa.find_all_valid_decks(node, version, production)

    for i, deck in enumerate(decks):
        if deck is not None:
            add_deck(deck)

        if any(i in subscribed for i in ('*', deck.id)):
            if deck.id not in accounts:
                load_key(deck.id)

            if not checkpoint(deck.id):
                try:
                    add_cards( pa.find_all_valid_cards(node, deck) )
                except:
                    continue
                init_state(deck.id)

        message(i)


def update_decks(txid):
    deck = pa.find_deck(node, txid, version)
    try:
        add_deck(deck)
    except KeyError:
        ''' Transaction most likely still in mempool '''
        pass

def update_state(deck_id):
    if not checkpoint(deck_id):
        DeckState(deck_id)
        return

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

            if not checkpoint(deck_id):
                remove_no_confirms(deck_id)
                add_cards( pa.find_all_valid_cards(node, deck) )
                init_state(deck.id)
                DeckState(deck_id)
        return {'walletnotify': True, 'deck_id':deck_id}
    else:
        return {'walletnotify': False, 'deck_id': deck_id}

def checkpoint(deck_id):
    ''' List all accounts and check if deck_id is loaded into the node'''
    accounts = node.listaccounts()

    if deck_id not in accounts:
        ''' if deck_id is not in accounts, load the key into the local node'''
        load_key(deck_id)

    ''' list all transactions for a particular deck '''
    txs = node.listtransactions(deck_id)
    ''' get deck object of current deck_id '''
    deck = pa.find_deck(node, deck_id, version)

    if isinstance(txs,list):
        ''' Make sure txs is a list rather than a dict with an error. Reverse list order.'''
        checkpoint = txs[::-1]
        ''' Get the most recent card transaction recorded in the database for the given deck '''
        try:
            _checkpoint = db.session.query(Card).filter(Card.deck_id == deck_id).order_by(Card.blocknum.desc()).first()
        except:
            _checkpoint = None

        if _checkpoint is None:
            return False

        elif _checkpoint.blockhash:
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
        tx = db.session.query(Card).filter(Card.blockhash == "").filter(Card.blocknum == 0).filter(Card.deck_id == deck_id).first()
    except:
        tx = None

    if tx is None:
        pass
    else:
        tx.delete()
        commit()


def init_pa():
    init_p2thkeys()
    init_decks()
    sys.stdout.write('PeerAssets version {} Initialized'.format(version))
    sys.stdout.flush()