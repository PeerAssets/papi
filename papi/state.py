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
        self.process_cards()

    @property
    def balances(self):
        return db.session.query(Balance).filter(Balance.short_id == self.short_id)

    def counter(self):

        Blocknum = self.balances.filter(Balance.account == 'blocknum')

        if Blocknum.first() is None:
            B = Balance( 'blocknum', 0, self.short_id )
            db.session.add(B)
            db.session.commit()
            Blocknum = self.balances.filter(Balance.account == 'blocknum')
        if Blocknum.first() is not None:
            self.cards = self.cards.filter(Card.blocknum > Blocknum.first().value)

    def process_issue(self, card):
        short_id = card.txid[0:10]

        def ONCE( amount: int = card.amount ):

            Issuer = self.balances.filter( Balance.account.contains( self.deck.issuer ) )

            if Issuer.first() is not None:
                if self.mode in IntFlag(2):
                    ''' Only first occurence of CardIssuance transaction is allowed '''
                    if Issuer.filter( Balance.account.contains( short_id ) ):
                        ''' CardIssue is from the first CardIssue txid (There can be multiple with same txid)'''
                        process_sender(amount, card)
                        process_receiver(amount, card)
                        return
                else:
                    process_sender(amount, card, tag=True)
                    process_receiver(amount, card)
                    return

            else:
                ''' Create a genesis CardIssue account then process receiver '''
                B = Balance( card.sender + short_id , -abs(amount), self.short_id)
                db.session.add(B)
                try:
                    db.session.commit()
                    process_receiver( amount, card)
                except IntegrityError:
                    pass

        def process_sender( amount, card, tag = False):
            ''' Add sender to db if the account doesn't exist and update sender balance '''
            Sender = self.balances.filter( Balance.account == card.sender + short_id * tag )

            if Sender.first() is not None:
                Sender.update( {"value" : Sender.first().value  - amount}, synchronize_session='fetch' )
            
            if Sender.first() is None:
                sender = card.sender + short_id * tag
                B = Balance( sender , -abs(amount), self.short_id)
                db.session.add(B)
                db.session.commit()

        def process_receiver( amount, card):
            ''' Add receiver to db if the account doesn't exist and update receiver balance ''' 
            Receiver = self.balances.filter( Balance.account == card.receiver )

            if Receiver.first() is not None:
                Receiver.update( {"value" : Receiver.first().value  + amount}, synchronize_session='fetch' )
            
            if Receiver.first() is None:
                B = Balance( card.receiver , amount, self.short_id)
                db.session.add(B)
                db.session.commit()

        def MULTI( amount: int = card.amount ):
            ''' Uses ONCE to create issuer id if it doesn't exist then
                updates the value by adding new issuance amounts '''

            Issuer = self.balances.filter( Balance.account.contains( self.deck.issuer ) )

            if Issuer.first() is not None:
                if Issuer.filter( Balance.account.contains( card.sender ) ).first() is not None:
                    process_sender( amount, card )
                else:
                    process_sender( amount, card, tag=True )

                process_receiver( amount, card )
                return
            else:
                ONCE()
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

    def process_burn(self, card):
        Receiver = self.balances.filter(Balance.account == 'CardBurn')
        Sender = self.balances.filter(Balance.account == card.sender)

        if Receiver.first() is not None:
            Receiver.first().update( {'value': Receiver.first().value + card.amount}, synchronize_session='fetch' )
        else:
            B = Balance('CardBurn', card.amount, self.short_id)
            db.session.add(B)
            db.session.commit()

        Sender.first().update( {'value': Sender.first().value - card.amount}, synchronize_session='fetch' )
        return

    def process_transaction(self, card):
        Sender = self.balances.filter(Balance.account == card.sender)

        if Sender.first() is None:
            return
        if Sender.first().value >= card.amount:
            Receiver = self.balances.filter(Balance.account == card.receiver)
            if card.ctype == "CardBurn":
                process_burn(card)
                return

            elif Receiver.first() is None:
                B = Balance(card.receiver, card.amount, self.short_id)
                db.session.add(B)
                db.session.commit()
            else:
                Receiver = self.balances.fiter(Balance.account == card.receiver)
                Receiver.first().update( {'value': Receiver.first().value + card.amount}, synchronize_session='fetch' )

            Sender = self.balances.filter(Balance.account == card.sender)
            Sender.first().update( {'value': Sender.first().value - card.amount}, synchronize_session='fetch' )
            db.session.commit()

        return

    def process_cards(self):
        Blocknum = self.balances.filter(Balance.account == 'blocknum')

        for card in self.cards:

            Blocknum.update( { "value": card.blocknum }, synchronize_session='fetch' )

            if (card.ctype == "CardIssue") and (self.deck.issuer == card.sender):
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
