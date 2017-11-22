import pypeerassets as pa
from models import Deck, Card, Balance, db
from state import DeckState, init_state
from sqlalchemy.exc import IntegrityError
from conf import *
import sys

node = pa.RpcNode(testnet=testnet)

def init_p2thkeys():

    from binascii import unhexlify
    n = 0

    if autoload:
        pa.pautils.load_p2th_privkey_into_local_node(node,production)

    for deck_id in subscribed:
        wif = pa.Kutil(privkey=unhexlify(deck_id), network=node.network).wif
        try:
            node.importprivkey(wif,deck_id)
            n += 1
        except Exception as e:
            print(e)
    return print('{} P2TH Key(s) Registered'.format(n))

def init_decks():
    n = 0

    def message(n):
        sys.stdout.flush()
        sys.stdout.write('{} Decks Loaded\r'.format(n))

    def add_deck(deck):
        if deck is not None:
            entry = db.session.query(Deck).filter(Deck.id == deck.id).first()
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
                    sys.stdout.write(card.txid +'\r')
                    sys.stdout.flush()
                    card_id = card.txid + str(card.blockseq) + str(card.cardseq)
                    entry = db.session.query(Card).filter(Card.id == card_id).first()   
                    if not entry:
                        C = Card( card_id, card.txid, card.cardseq, card.receiver[0], card.sender, card.amount[0], card.type, card.blocknum, card.blockseq, card.deck_id )
                        db.session.add(C)
                    db.session.commit()
            sys.stdout.flush()

    if not autoload:
        decks = [pa.find_deck(node,txid,version)[0] for txid in subscribed]

        for deck in decks:
            if deck is not None:
                add_deck(deck)
                add_cards( pa.find_card_transfers(node, deck) )
                n += 1
                message(n)

    else:
        decks = pa.find_all_valid_decks(node, 1 , True)
        while True:
            try: 
                deck = next(decks)
                add_deck( deck )
                if deck.id in subscribed:
                    add_cards( pa.find_card_transfers(node, deck ) )
                n += 1
                message(n)
            except StopIteration:
                break

def init_pa():
    init_p2thkeys()
    init_decks()
    init_state()


    sys.stdout.write('PeerAssets version {} Initialized'.format(version))
    sys.stdout.flush()