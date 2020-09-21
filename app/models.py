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
        #db.session.commit()

    def unknown(self):
        ease = self.ease / self.deck.multiplier
        if ease > 1:
            self.ease = math.floor(ease)
        else:
            self.ease = 1
        self.priority = True
        self.last_time = datetime.now()
        self.deck.active_card_id = None
        #db.session.commit()


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    card_number = db.Column(db.Integer, default=20)  # old cards per go and intial number of cards
    new_card_number = db.Column(db.Integer, default=10)  # new cards per go
    card_counter = db.Column(db.Integer, default=0)
    shuffle_interval = db.Column(db.Integer, default=20)
    shuffle_counter = db.Column(db.Integer, default=0)
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
        #max_ease = max(self.seen_cards, key=lambda c: c.ease).ease
        #max_time = max(self.seen_cards, key=lambda c: c.last_time).last_time
        min_time = min(self.seen_cards, key=lambda c: c.last_time).last_time
        #delta = max_time - min_time

        delta_cards = defaultdict(list)
        for c in self.seen_cards:
            delta = (c.last_time - min_time).total_seconds()
            delta_cards[delta*c.ease].append(c)
            #print(delta)
            if not c.priority:
                c.learning = False

        counter = 0
        #breakpoint()
        while counter < self.card_number:
            #print(len(delta_cards), counter)
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

    def get_priority_cards(self):
        return [c for c in self.seen_cards if c.priority]

    def organise_cards(self):
        self.seen_cards = [c for c in self.cards if c.last_time is not None]
        self.unseen_cards = [c for c in self.cards if c.last_time is None]
        if self.shuffle_counter == self.card_number + self.new_card_number:
            self.shuffle()
            self.shuffle_counter = 0
        self.learning_cards = [c for c in self.cards if c.learning]

    def get_seen_card(self):
        if self.seen_cards:
            review_point = datetime.now() - timedelta(
                minutes=math.sqrt(len(self.seen_cards))
                )
            fl = [c for c in self.seen_cards if c.last_time < review_point]
            #  oldest_10 = self.seen_cards.sort(key=lambda c: c.last_time)
            if fl:
                return min(fl, key=lambda c: c.ease)

    def get_learning_card(self):
        if self.learning_cards:
            cards = [c for c in self.learning_cards if c.priority is False]
            if cards:
                return min(cards, key=lambda c: c.ease)
            else:
                return min(self.learning_cards, key=lambda c: c.ease)

    def get_unseen_card(self):
        if self.unseen_cards:
            return self.unseen_cards[0]

    def get_priority_card(self):
        """
        Returns the priority card with the lowest ease.
        """
        cards = [c for c in self.seen_cards if c.priority]
        if cards:
            return min(cards, key=lambda c: c.ease)

    def get_next_card(self):
        card = None
        if self.card_counter >= self.entry_interval:
            card = self.get_unseen_card()
            self.card_counter = 0
        if card is None:
            self.card_counter += 1
            if self.card_counter in (4, 2):
                card = self.get_priority_card()
        if card is None:
            self.shuffle_counter += 1
            card = self.get_learning_card()
        if card is None:
            card = self.get_priority_card() or self.get_unseen_card()
        return card

    def play_go(self):
        #breakpoint()
        self.organise_cards()
        if self.active_card_id is None:
            if len(self.seen_cards) < self.card_number:
                # first entry to deck
                if len(self.learning_cards) == 0:
                    # get self.card_number of cards and add them to learning
                    for c in self.unseen_cards[:self.card_number]:
                        c.learning = True
                        self.learning_cards.append(c)
                self.active_card_id = self.get_learning_card().id
                self.shuffle_counter += 1
            else:
                self.active_card_id = self.get_next_card().id
            # print(self.shuffle_counter, len(self.seen_cards))
        if self.shuffle_counter == 0:
            db.session.commit()

    def play_outcomes(self, outcomes):
        """
        plays as many cards as there are in outcomes
        outcomes :
        {
            '1': {'id': '2516', 'result': 'x'},
            '2': {'id': '2517', 'result': 'z'},
            'deck_id': '6'
        }

        """
        for out in outcomes:
            self.play_go()
            card = Card.query.get(self.active_card_id)
            if out is True:
                card.known()
            elif out is False:
                card.unknown()


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


