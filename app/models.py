import random
from app import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from datetime import datetime, timedelta
import math
import abc
from collections import defaultdict

Base = declarative_base()

# carddeck = db.Table('carddeck',
#     db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
#     db.Column('deck_id', db.Integer, db.ForeignKey('deck.id'))
# )


class Card(db.Model, Base):
    __metaclass__ = abc.ABCMeta
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(50))
    ease = db.Column(db.Integer, default=1)
    last_time = db.Column(db.DateTime, default=None)
    priority = db.Column(db.Boolean, default=False)
    learning = db.Column(db.Boolean, default=False)  # for reprioritisation
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    deck = db.relationship('Deck', back_populates='cards')

    __mapper_args__ = {
        'polymorphic_identity': 'card',
        'polymorphic_on': type
    }

    @abc.abstractmethod
    def get_questions(self):
        return

    @abc.abstractmethod
    def get_answers(self):
        return

    def get_dict(self):
        return {
            'id': self.id,
            'questions': self.get_questions(),
            'answers': self.get_answers()
        }

    def known(self):
        self.ease *= self.deck.multiplier
        if self.priority is True:
            self.priority = False
        else:
            self.learning = False
        self.last_time = datetime.now()
        self.deck.active_card_id = None

    def unknown(self):
        ease = self.ease / self.deck.multiplier
        if ease > 1:
            self.ease = math.floor(ease)
        else:
            self.ease = 1
        self.priority = True
        self.last_time = datetime.now()
        self.deck.active_card_id = None


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    card_number = db.Column(db.Integer, default=20)  # old cards per go and initial number of cards
    new_card_number = db.Column(db.Integer, default=10)  # new cards per go
    card_counter = db.Column(db.Integer, default=0)
    multiplier = db.Column(db.Integer, default=2)  # ease multiplier
    entry_interval = db.Column(db.Integer, default=5)  # new card entry
    last_date = db.Column(db.Date, default=None)

    cards = db.relationship('Card', back_populates='deck')
    active_card_id = db.Column(db.Integer, default=None)

    def shuffle(self):
        self.organise_cards()
        if len(self.seen_cards) == 0:
            for c in self.unseen_cards[0:self.card_number]:
                c.learning = True
            return

        min_time = min(self.seen_cards, key=lambda c: c.last_time).last_time
        delta_cards = defaultdict(list)
        for c in self.seen_cards:
            delta = (c.last_time - min_time).total_seconds()
            delta_cards[delta*c.ease].append(c)
            if not c.priority:
                c.learning = False

        counter = 0
        while counter < self.card_number:
            for c in delta_cards[min(delta_cards)]:
                c.learning = True
                counter += 1
            del delta_cards[min(delta_cards)]

        for c in self.unseen_cards[0:self.new_card_number]:
            c.learning = True

    def __repr__(self):
        return '<Deck "{}">'.format(self.name)

    def get_learning_cards(self):
        if len([c for c in self.cards if c.learning]) == 0:
            self.shuffle()
        return [c for c in self.cards if c.learning]

    def organise_cards(self):
        self.seen_cards = [c for c in self.cards if c.last_time is not None]
        self.unseen_cards = [c for c in self.cards if c.last_time is None]
        self.learning_cards = [c for c in self.cards if c.learning]

    def play_outcomes(self, outcomes):
        """
        plays as many cards as there are in outcomes
        outcomes :
        {
            '1': {'id': '2516', 'result': 'x'},
            '2': {'id': '2517', 'result': 'z'},
            'deck_id': '6' # not here?
        }

        """
        for i in range(0, len(outcomes) - 1):
            outcome_row = outcomes[str(i+1)]
            card_id = int(outcome_row.get('id'))
            card = Card.query.get(card_id)
            result = outcome_row.get('result')
            if result == 'z':
                card.known()
            elif result == 'x':
                card.unknown()

        db.session.commit()


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


