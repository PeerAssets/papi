import pypeerassets as pa
from time import sleep
from requests.exceptions import ConnectionError
from models import Deck, Card, Balance, db
from state import DeckState, init_state
from sqlalchemy.exc import IntegrityError
from conf import *
import sys


def node_sync(node):

    if not isinstance(node, pa.RpcNode):
        ''' Initiate RpcNode'''
        node = pa.RpcNode(testnet=testnet, username=rpc_username, password=rpc_password,
                          ip=rpc_host, port=rpc_port)
    info = node.getinfo()

    if info['connections']:
        ''' Making sure node has connections'''
        recent = []

        for i in node.getpeerinfo():
            ''' Appending connected peers current blockheights'''
            recent.append(i['startingheight'])

        if info['blocks'] < max(recent) - 500:
            ''' Checking if the local node is sync'd at least 500 blocks behind peer with max blocks'''
            sys.stdout.write('\rLocal node is not completely synced. Block {} of {}'.format(info['blocks'],max(recent)))
            return {'synced': False ,'node': node}
        else:
            ''' Node is now synced and the function returns True to begin papi initialization'''
            sys.stdout.write('\r\nConnected : {}\nTestnet = {}\n'.format(info['version'], info['testnet']))
            return {'synced': True ,'node': node}

''' Connection attempts counter'''
attempts = 0

while True:
    node = None

    try:
        connection = node_sync(node)
        if connection is not None and connection['synced']:
            ''' if node is synced with the network then break and continue papi initialization'''
            node = connection['node']
            break
        else:
            ''' if node is not synced then wait 3 seconds and try again '''
            sleep(3)
            continue

    except (FileNotFoundError, ConnectionError, Exception) as e:
        attempts += 1
        if attempts > max_attempts:
            raise Exception('Max connection attempts reached. Stopping papi...')

        if isinstance(e,FileNotFoundError):
            ''' This will occur if local node configuration file is not created/defined with correct RPC parameters'''
            sys.stdout.write('Waiting for RPC parameters\r')
        elif isinstance(e, ConnectionError):
            ''' This will be occur when the local node is not running'''
            sys.stdout.write('Waiting for connection to local node. Attempt(s): {} of {}\r'.format(attempts, max_attempts))
        else:
            sys.stdout.write(str(e) + '\r')

        sys.stdout.flush()
        sleep(3)
        continue


def init_p2thkeys():

    if autoload:
        pa.pautils.load_p2th_privkey_into_local_node(node, production)


def add_deck(deck):
    if deck is not None:
        entry = db.session.query(Deck).filter(Deck.id == deck.id).first()
        if '*' in subscribed:
            subscribe = True
        else:
            subscribe = deck.id in subscribed

        if not entry:
            try:
                D = Deck( deck.id, deck.name, deck.issuer, deck.issue_mode, deck.number_of_decimals, subscribe)
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
                entry = db.session.query(Card).filter(Card.txid == card.txid).filter(Card.blockseq == card.blockseq).filter(Card.cardseq == card.cardseq).first()
                if not entry:
                    C = Card( card.txid, card.blockhash, card.cardseq, card.receiver[0], card.sender, card.amount[0], card.type, card.blocknum, card.blockseq, card.deck_id, False )
                    db.session.add(C)
                db.session.commit()

def load_key(deck_id):
    from binascii import unhexlify
    try:
        wif = pa.Kutil(privkey=unhexlify(deck_id), network=node.network).wif
        node.importprivkey( wif, deck_id)
    except Exception as e:
        print(e)

def init_decks():
    accounts = node.listaccounts()
    n = 0

    def message(n):
        sys.stdout.flush()
        sys.stdout.write('\r{} Decks Loaded\r'.format(n))

    if not autoload:
        decks = [pa.find_deck(node,txid,version) for txid in subscribed]

        for deck in decks:
            if deck is not None:
                if deck.id not in accounts:
                    load_key(deck.id)
                add_deck(deck)
                try:
                    if not checkpoint(deck.id):
                        add_cards( pa.find_card_transfers(node, deck) )
                        init_state(deck.id)
                except:
                    continue
                n += 1
                message(n)

    else:
        decks = pa.find_all_valid_decks(node, version, production)
        while True:
            try: 
                deck = next( decks )
                if deck.id not in accounts:
                    load_key(deck.id)
                add_deck( deck )
                if not checkpoint(deck.id):
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
    deck_id = None

    if 'details' in deck.keys():
         owneraccounts = [details['account'] for details in deck['details'] if details['account']]
         if len(owneraccounts):
             deck_id = [details['account'] for details in deck['details'] if details['account']][0]

    if deck_id is not None:
        if deck_id in ('PAPROD','PATEST'):
            update_decks(txid)
        elif deck_id in subscribed or subscribed == ['*']:
            deck = pa.find_deck(node, deck_id, version)
            if not checkpoint(deck_id):
                add_cards( pa.find_card_transfers(node, deck) )
                init_state(deck.id)
                DeckState(deck_id)
        return {'deck_id':deck_id}
    else:
        return

def update_state(deck_id):
    if not checkpoint(deck_id):
        DeckState(deck_id)
        return

def checkpoint(deck_id):
    txs = node.listtransactions(deck_id)
    accounts = node.listaccounts()
    if deck_id not in accounts:
        load_key(deck_id)
    if isinstance(txs,list):
        checkpoint = txs[::-1]
        _checkpoint = db.session.query(Card).filter(Card.deck_id == deck_id).order_by(Card.blocknum.desc()).first()

        if checkpoint:
            for i in range(len(checkpoint)):
                if 'blockhash' in checkpoint: #Check if key exists first
                    if checkpoint[i]['blockhash'] == _checkpoint:
                        return True

                tx = checkpoint[i]['txid']
                rawtx = node.getrawtransaction(tx,1)
                deck = pa.find_deck(node, deck_id, version)
                try:
                    pa.validate_card_transfer_p2th(deck, rawtx)
                    return _checkpoint.blockhash == checkpoint[i]['blockhash']
                except Exception:
                    continue

            return False
    return False

def init_pa():
    init_p2thkeys()
    init_decks()

    sys.stdout.write('PeerAssets version {} Initialized'.format(version))
    sys.stdout.flush()