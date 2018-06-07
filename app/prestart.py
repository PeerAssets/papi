import pypeerassets as pa
from main import node, add_deck, add_cards, validate
from utils.state import init_state
from sys import stdout


accounts = node.listaccounts()

def message(n):
    print('\r{} Decks Loaded\r'.format(n))
    stdout.flush()

for i, deck in enumerate( pa.find_all_valid_decks(node,1,1) ):

    add_deck(deck)
    message(i)
    if deck.id not in accounts:
        validate(deck)

    try:
        add_cards(deck)
    except IndexError:
        continue
        
    init_state(deck.id)