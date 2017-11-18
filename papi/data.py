import pypeerassets as pa
from pypeerassets.paproto_pb2 import DeckSpawn, CardTransfer
from models import Deck, Card, db
from sqlalchemy.exc import IntegrityError
from conf import *

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
    import sys
    n = 0

    def message(n):
        sys.stdout.flush()
        sys.stdout.write('{} Decks Loaded\r'.format(n))

    def add_deck(deck):
        entry = db.session.query(Deck).filter(Deck.id == deck.id).first()
        subscribe = deck.id in subscribed     
        if not entry:
            D = Deck( deck.id, deck.name, deck.issuer, pa.pautils.issue_mode_to_enum(DeckSpawn(), deck.issue_mode), deck.number_of_decimals, subscribe )
            try:
                db.session.add(D)
                db.session.commit()
            except IntegrityError as e:
                print(e)
                pass
        else:
            db.session.query(Deck).filter(Deck.id == deck.id).update({"subscribed": subscribe})
            db.session.commit()

    def add_cards(cards):
        n = 0
        if cards is None:
            return
        for card in cards:
            card_id = card.txid + str(card.blockseq) + str(card.cardseq)
            n += 1
            entry = db.session.query(Card).filter(Card.id == card_id).first()   
            if not entry:
                C = Card( card_id, card.txid, card.cardseq, card.receiver[0], card.sender, card.amount[0], card.type, card.blocknum, card.blockseq, card.deck_id )
                try:
                    db.session.add(C)
                    db.session.commit()
                except (IntegrityError, Exception) as e:
                    print(e)
                    pass


    if not autoload:
        decks = [pa.find_deck(node,txid,version)[0] for txid in subscribed]

        for deck in decks:
            add_deck(deck)
            if deck.id in subscribed:
                add_cards( pa.find_card_transfers(node, deck) )
            n += 1
            message(n)

    else:
        from itertools import tee
        decks = pa.find_all_valid_decks(node, 1 , True)
        decks, _decks = tee(decks,2)
        while True:
            try: 
                deck = next(decks)
                add_deck( deck )
                if deck.id in subscribed:
                    add_cards( pa.find_card_transfers(node, next(_decks ) ) )
                n += 1
                message(n)
            except StopIteration:
                break

#def init_cards():
#    for deck_id in subscribed:

def init_pa():
    init_p2thkeys()
    init_decks()
    #init_cards()
    print('PeerAssets version {} Initialized'.format(version))



        

        
