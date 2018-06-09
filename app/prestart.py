import pypeerassets as pa
from main import node, add_deck, add_cards, validate, init_p2thkeys
from utils.state import init_state
from sys import stdout
from conf import subscribed

init_p2thkeys()
accounts = node.listaccounts()
total = sum( 1 for deck in  pa.find_all_valid_decks(node,1,1) )

def message(n):
    print('{} of {} Decks Loaded'.format(n+1, total))
    stdout.flush()

for n, deck in enumerate( pa.find_all_valid_decks(node,1,1) ):
    
    if not any(deck_id in subscribed for deck_id in ('*', deck.id)):
        continue
    else:
        add_deck(deck)
        message(n)
        if deck.id not in accounts:
            validate(deck)

        try:
            add_cards(deck)
            init_state(deck.id)
        except IndexError:
            continue
