import random
from app import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from datetime import datetime


Base = declarative_base()

# carddeck = db.Table('carddeck',
#     db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
#     db.Column('deck_id', db.Integer, db.ForeignKey('deck.id'))
# )


class Card(db.Model, Base):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(50))
    ease = db.Column(db.Integer, default=1)
    last_time = db.Column(db.DateTime, default=None)
    priority = db.Column(db.Boolean, default=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    deck = db.relationship('Deck', back_populates='cards')

    __mapper_args__ = {
        'polymorphic_identity': 'card',
        'polymorphic_on': type
    }

    def known(self):
        self.ease *= self.deck.multiplier
        self.priority = False
        self.last_time = datetime.now()
        db.session.commit()
    
    def unknown(self):
        self.ease /= self.deck.multiplier
        self.priority = True
        self.last_time = datetime.now()
        db.session.commit()


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    cards = db.relationship('Card', back_populates='deck')
    card_number = db.Column(db.Integer, default=20)  # new cards per go
    card_counter = db.Column(db.Integer, default=0)
    multiplier = db.Column(db.Integer, default=2)  # ease multiplier
    entry_interval = db.Column(db.Integer, default=5)  # new card entry
    last_date = db.Column(db.Date, default=None)

    seen_cards = []
    unseen_cards = []

    def organise_cards(self):
        self.seen_cards = [c for c in self.cards if c.last_time is not None]
        self.unseen_cards = [c for c in self.cards if c.last_time is None]
        
    def __repr__(self):
        return '<Deck "{}">'.format(self.name)

    def see_cards(self):
        return random.sample(self.cards, 20)
    
    def get_seen_card(self):
        if self.seen_cards:
            return self.seen_cards.pop(
                min(self.seen_cards, key=lambda c: c.ease)
            )
    
    def get_unseen_card(self):
        if self.unseen_cards:
            return self.unseen_cards.pop(
                min(self.unseen_cards, key=lambda c: c.ease)
            )

    def get_priority_card(self):
        cards = [c for c in self.seen_cards if c.priority]
        if cards:
            return self.seen_cards.pop(
                min(cards, key=lambda c: c.ease)
            )
        
    def get_next_card(self):
        if self.card_counter >= self.entry_interval:
            card = self.get_unseen_card()
            self.card_counter = 0
        if not card:
            self.card_counter += 1
            if self.card_counter in (4, 2):
                card = self.get_priority_card()
        if not card:
            card = self.get_seen_card()
        return card
    
    def play(self):
        if not self.seen_cards and not self.unseen_cards:
            self.organise_cards()
        if len(self.seen_cards) <= self.card_number:
            return self.get_unseen_card()
        return self.get_next_card()
        

class Word(Card):
    __tablename__ = 'word'
    id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    zi_simp = db.Column(db.String(12), index=True)
    zi_trad = db.Column(db.String(12), index=True)
    pinyin_number = db.Column(db.String(80), index=True)
    pinyin_tone = db.Column(db.String(80), index=True)
    english = db.Column(db.String(160))
    hsk = db.Column(db.Integer)

    def __repr__(self):
        return '<{}>'.format(self.zi_simp)

    __mapper_args__ = {
        'polymorphic_identity': 'word',
    }

    def get_questions(self):
        q = (
            self.zi_simp,
            self.zi_trad
        )
        return q

    def get_answers(self):
        a = (
            self.pinyin_tone,
            self.english
        )
        return a


# class Sentence(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     zi = db.Column(db.String(120), index=True, unique=True)
#     pinyin = db.Column(db.String(80), index=True)
#     english = db.Column(db.String(160))


