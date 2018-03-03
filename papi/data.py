import pypeerassets as pa
from models import Deck, Card, Balance, db
from state import DeckState, init_state
from sqlalchemy.exc import IntegrityError
from conf import *
import sys

node = pa.RpcNode(testnet=testnet, username=rpc_username, password=rpc_password,
                  ip=rpc_host, port=rpc_port)


def init_p2thkeys():
    n = 0

    if autoload:
        pa.pautils.load_p2th_privkey_into_local_node(node,production)

def add_deck(deck):
    if deck is not None:
        entry = db.session.query(Deck).filter(Deck.id == deck.id).first()
        if '*' in subscribed:
            subscribe = True
        else:
            subscribe = deck.id in subscribed
        

        if not entry:
            try:
                D = Deck( deck.id, deck.name, deck.issuer, deck.issue_mode, deck.number_of_decimals, subscribe )
                db.session.add(D)
                db.session.commit()
            except Exception as e:
                print(e)
                pass
        else:
            db.session.query(Deck).filter(Deck.id == deck.id).update({"subscribed": subscribe})
            db.session.commit()

def add_cards(cards):
    if cards is not None:
        for cardset in cards:
            for card in cardset:
                card_id = card.txid + str(card.blockseq) + str(card.cardseq)
                entry = db.session.query(Card).filter(Card.id == card_id).first()   
                if not entry:
                    C = Card( card_id, card.txid, card.cardseq, card.receiver[0], card.sender, card.amount[0], card.type, card.blocknum, card.blockseq, card.deck_id )
                    db.session.add(C)
                db.session.commit()

def load_key(deck_id):
    from binascii import unhexlify
    wif = pa.Kutil(privkey=unhexlify(deck_id), network=node.network).wif
    node.importprivkey(wif,deck_id)

def init_decks():
    accounts = node.listaccounts()
    n = 0

    def message(n):
        sys.stdout.flush()
        sys.stdout.write('{} Decks Loaded\r'.format(n))

    if not autoload:
        decks = [pa.find_deck(node,txid,version) for txid in subscribed]

        for deck in decks:
            if deck is not None:
                if deck.id not in accounts:
                    load_key(deck.id)
                add_deck(deck)
                try:
                    add_cards( pa.find_card_transfers(node, deck) )
                except:
                    continue

                init_state(deck.id)
                n += 1
                message(n)

    else:
        decks = pa.find_all_valid_decks(node, 1, True)
        while True:
            try: 
                deck = next( decks )
                add_deck( deck )
                if deck.id not in accounts:
                    load_key(deck.id)
                try:
                    if '*' in subscribed:
                        add_cards( pa.find_card_transfers( node, deck ) )
                    elif deck.id in subscribed:
                        add_cards( pa.find_card_transfers( node, deck ) )
                except:
                    continue

                init_state(deck.id)
                n += 1
                message(n)
            except StopIteration:
                break

def update_decks(txid):
    deck = pa.find_deck(node, txid, version)
    add_deck(deck)
    return

def which_deck(txid):
    deck = node.gettransaction(txid)
    deck_id = [details['account'] for details in deck['details'] if details['account']][0]
    if deck_id:
        if deck_id in ('PAPROD','PATEST'):
            update_decks(txid)
        elif deck_id in subscribed:
            deck = pa.find_deck(node, deck_id, version)
            add_cards( pa.find_card_transfers(node, deck) )
            DeckState(deck_id)
        return {'deck_id':txid}
    else:
        return

def update_state(deck_id):
    DeckState(deck_id)
    return

def init_pa():
    init_p2thkeys()
    init_decks()

    sys.stdout.write('PeerAssets version {} Initialized'.format(version))
    sys.stdout.flush()

