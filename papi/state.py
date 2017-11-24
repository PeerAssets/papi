from enum import IntFlag
from data import *
from conf import subscribed

class DeckState:

    def __init__(self, deck_id: str):

        self.deck = db.session.query(Deck).filter(Deck.id == deck_id).first()
        self.short_id = deck_id[0:10]
        self.mode = IntFlag(self.deck.issue_mode)
        self.issuer = self.deck.issuer
        self.cards = db.session.query(Card).filter(Card.deck_id == deck_id).order_by(Card.blocknum,Card.blockseq,Card.cardseq)
        self.counter()
        self.process()

    @property
    def balances(self):
        return db.session.query(Balance).filter(Balance.short_id == self.short_id)

    def counter(self):

        Blocknum = db.session.query(Balance).filter(Balance.account == 'blocknum')

        if Blocknum.first() is None:
            B = Balance( 'blocknum', 0, self.short_id )
            db.session.add(B)
            db.session.commit()
            Blocknum = db.session.query(Balance).filter(Balance.account == 'blocknum')
        if Blocknum.first() is not None:
            self.cards = self.cards.filter(Card.blocknum >= Blocknum.first().value)

    def process_issue(self, card):

        card_id = card.txid[0:10]

        def ONCE( amount: int = card.amount ):
            ''' Create an entry and sets value if issuer id does not exist.'''

            Issuer = self.balances.filter( Balance.account.contains( card.sender ) )

            if card.sender == self.deck.issuer :

                if Issuer.first() is None:
                    B = Balance( card.sender + card_id , 0, self.short_id)
                    db.session.add(B)
                    db.session.commit()
                    Issuer = self.balances.filter( Balance.account.contains( card_id ) )

                if Issuer is not None: 
                    Receiver = self.balances.filter( Balance.account.contains( card.receiver ) )

                    if Receiver.first() is None:
                        B = Balance( card.receiver , amount, self.short_id)
                        db.session.add(B)
                        db.session.commit()
                        Receiver = self.balances.filter( Balance.account.contains( card.receiver ) )

                    if Receiver.first() is not None:
                        Receiver.update( {"value" : Receiver.first().value  + amount} )


        def MULTI( amount: int = card.amount ):
            ''' Uses ONCE to create issuer id if it doesn't exist then
                updates the value by adding new issuance amounts '''

            Issuer = self.balances.filter(Balance.account.contains(self.deck.issuer))
            if Issuer.first() is None:
                ONCE()
                Issuer = self.balances.filter(Balance.account.contains(self.deck.issuer))
            if Issuer.first() is not None:
                Issuer.first().update( {"value" : Balance.value + amount} )
                return

        if self.mode in IntFlag(2):
            ''' ONCE '''
            ONCE()
                
        elif self.mode in IntFlag(4):
            ''' MULTI '''
            MULTI()

        elif self.mode in IntFlag(8):
            ''' MONO '''
            MULTI(amount=1)

        db.session.commit()
        return

    def process_transaction(self, card):
        Sender = self.balances.filter(Balance.account == card.sender)

        if Sender.first() is None:
            return
        elif Sender.first() is not None:
            return
        else:
            Receiver = self.balances.filter(Balance.account == card.receiver)
            if Receiver.first() is None:
                B = Balance(card.receiver, card.amount, self.short_id)
                db.session.add(B)
                db.session.commit()
            else:
                Receiver = self.balances.fiter(Balance.account == card.receiver)
                Receiver.first().update( {'value': Receiver.first().value + card.amount})

            Sender = self.balances.filter(Balance.account == card.sender)
            Sender.first().update( {'value': Sender.first().value - card.amount})
            db.session.commit()

        return

    def process(self):
        Blocknum = db.session.query(Balance).filter(Balance.account == 'blocknum')

        for card in self.cards:

            Blocknum.update( { "value": card.blocknum } )

            if card.ctype == "CardIssue":
                self.process_issue( card )

            else:
                if self.mode in IntFlag(16):
                    if ( card.sender == self.deck.issuer ):
                        process_transaction(card)

                elif self.mode in IntFlag(52):
                    pass # Need to include blocktime into db per card
                
                else:
                    process_transaction(card)

def init_state():
    for deck_id in subscribed:
        DeckState(deck_id)
    return
