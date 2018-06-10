from pypeerassets.protocol import IssueMode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Deck, Card, Balance
from app import *
from conf import subscribed


engine = create_engine(db_engine)
Session = sessionmaker(bind=engine)
session = Session()


def commit():
    try:
        session.commit()
    except:
        session.rollback()


class DeckState:

    def __init__(self, deck_id: str):
        self.deck = session.query(Deck).filter(Deck.id == deck_id).first()
        self.short_id = deck_id[0:10]
        try:
            self.mode = IssueMode(self.deck.issue_mode).name
        except ValueError:
            return
        self.issuer = self.deck.issuer
        self.cards = session.query(Card).filter(Card.deck_id == deck_id).order_by(Card.blocknum,Card.blockseq,Card.cardseq)
        self.counter()
        self.process_cards()

    @property
    def balances(self):
        ''' Get all balances that correspond with the current deck '''
        return session.query(Balance).filter(Balance.short_id == self.short_id)

    def counter(self):
        ''' Get the block number that the balances for this account were last updated'''  
        Blocknum = self.balances.filter(Balance.account == 'blocknum')

        if Blocknum.first() is None:
            ''' If this deck does not have a 'blocknum' account in database then create one '''
            B = Balance( 'blocknum', 0, self.short_id, '' )
            session.add(B)
            commit()
            Blocknum = self.balances.filter(Balance.account == 'blocknum')

        if Blocknum.first() is not None:
            ''' Only concerned with cards that are before the last update to balances of this deck '''
            self.cards = self.cards.filter(Card.blocknum > Blocknum.first().value)

    def process_issue(self, card, amount = None):
        c_short_id = card.txid[0:10]

        if amount is not None:
            amount = amount
        else:
            amount = card.amount

        def ONCE( amount: int = amount ):
            ''' Set Issuer object to a query of all accounts containing the deck issuing address '''
            Issuer = self.balances.filter( Balance.account.contains( self.deck.issuer ) )

            if Issuer.first() is not None:
                ''' There is already an entry containing the deck issuing address '''

                if self.mode == 'ONCE':
                    ''' If issue mode of the deck is ONCE then only first occurence
                        of CardIssuance transaction is allowed '''

                    if Issuer.filter( Balance.account.contains( c_short_id ) ).first() is not None:
                        ''' Here we are checking to see if this card is a part of the first issuance transaction
                            (There can be multiple with same txid)'''

                        process_sender(amount, card)
                        process_receiver(amount, card)
                        _card = session.query(Card).filter(Card.txid == card.txid).filter(Card.blockseq == card.blockseq).filter(Card.cardseq == card.cardseq).first()
                        _card.valid = True
                        commit()
                        return
                    else:
                        return
                else:
                    ''' Continue processing issuance since it does not contain ONCE issue mode'''

                    process_sender( amount, card )
                    process_receiver( amount, card )
                    _card = session.query(Card).filter(Card.txid == card.txid).filter(Card.blockseq == card.blockseq).filter(Card.cardseq == card.cardseq).first()
                    _card.valid = True
                    commit()
                    return

            elif Issuer.first() is None:
                ''' Create a genesis CardIssue account then process receiver '''
                B = Balance( self.deck.issuer + c_short_id , -abs(amount), self.short_id, card.blockhash)
                try:
                    session.add(B)
                    commit()
                    process_receiver( amount, card)
                    _card = session.query(Card).filter(Card.txid == card.txid).filter(Card.blockseq == card.blockseq).filter(Card.cardseq == card.cardseq).first()
                    _card.valid = True
                    commit()
                except Exception as e:
                    print(e+'\r')
                    pass

        def process_sender( amount, card ):
            ''' Add sender to db if the account doesn't exist and update sender balance '''

            Sender = self.balances.filter( Balance.account.contains( card.sender + c_short_id) )

            if Sender.first() is not None:
                ''' If there is already an existing address for the sender '''
                Sender.update( {"value" : Sender.first().value  - abs(amount), "checkpoint": card.blockhash }, synchronize_session='fetch' )
            
            elif Sender.first() is None:
                B = Balance( card.sender + c_short_id , -abs(amount), self.short_id, card.blockhash)
                session.add(B)
                commit()

        def process_receiver( amount, card):
            ''' Add receiver to db if the account doesn't exist and update receiver balance ''' 
            Receiver = self.balances.filter( Balance.account == card.receiver )

            if Receiver.first() is not None:
                Receiver.update( {"value" : Receiver.first().value  + amount, "checkpoint": card.blockhash}, synchronize_session='fetch' )
            
            if Receiver.first() is None:
                B = Balance( card.receiver , amount, self.short_id, card.blockhash)
                session.add(B)
                commit()

        def MULTI( amount: int = card.amount ):
            ''' Uses ONCE to create issuer id if it doesn't exist then
                updates the value by adding new issuance amounts '''

            Issuer = self.balances.filter( Balance.account.contains( self.deck.issuer ) )

            if Issuer.first() is not None:
                if Issuer.filter( Balance.account.contains( card.sender ) ).first() is not None:
                    process_sender( amount, card )
                else:
                    process_sender( amount, card )

                process_receiver( amount, card )
                _card = session.query(Card).filter(Card.txid == card.txid).filter(Card.blockseq == card.blockseq).filter(Card.cardseq == card.cardseq).first()
                _card.valid = True
                commit()
                return
            else:
                ONCE()
                return


        if self.mode == IssueMode(2).name:
            ''' ONCE '''
            ONCE()
                
        elif self.mode == IssueMode(4).name:
            ''' MULTI '''
            MULTI()

        elif self.mode == IssueMode(8).name:
            ''' MONO '''
            MULTI(amount=1)

        commit()
        return

    def process_burn(self, card, amount: int = None):

        if amount is None:
            amount = card.amount

        Receiver = self.balances.filter(Balance.account == 'CardBurn')
        Sender = self.balances.filter(Balance.account == card.sender)

        if Receiver.first() is not None:
            Receiver.update( {'value': Receiver.first().value + amount}, synchronize_session='fetch' )
        else:
            B = Balance('CardBurn', amount, self.short_id, card.blockhash)
            session.add(B)
            commit()

        Sender.update( {'value': Sender.first().value - amount}, synchronize_session='fetch' )
        return

    def process_transaction(self, card, amount: int = None):

        if amount is None:
            amount = card.amount

        Sender = self.balances.filter(Balance.account == card.sender)

        if Sender.first() is None:
            return
        if Sender.first().value >= amount:
            Receiver = self.balances.filter(Balance.account == card.receiver)
            if card.ctype == "CardBurn":
                self.process_burn(card)
                return

            elif Receiver.first() is None:
                B = Balance(card.receiver, amount, self.short_id, card.blockhash)
                session.add(B)
                commit()
            else:
                Receiver = self.balances.filter(Balance.account == card.receiver)
                Receiver.update( {'value': Receiver.first().value + amount}, synchronize_session='fetch' )

            Sender = self.balances.filter(Balance.account == card.sender)
            Sender.update( {'value': Sender.first().value - amount}, synchronize_session='fetch' )
            commit()

        return

    def process_cards(self):
        Blocknum = self.balances.filter(Balance.account == 'blocknum')

        for card in self.cards:

            Blocknum.update( { "value": card.blocknum }, synchronize_session='fetch' )

            if (card.ctype == "CardIssue") and (self.deck.issuer == card.sender):
                if self.mode != IssueMode(8).name:
                    self.process_issue( card )
                else:
                    self.process_issue( card, amount=1)

            else:
                if self.mode == IssueMode(16).name:
                    if ( card.sender == self.deck.issuer ):
                        self.process_transaction(card)

                elif self.mode == IssueMode(52).name:
                    pass # Need to include blocktime into db per card
                
                else:
                    self.process_transaction(card)
    

def init_state(deck_id):
    try:
        DeckState(deck_id)
        session.close()
    except Exception as e:
        print(e)
        pass
    return
