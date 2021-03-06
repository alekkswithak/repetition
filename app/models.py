import math
import abc
from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


association_table = db.Table('association',
    db.Column('user_deck_id', db.Integer, db.ForeignKey('user_deck.id')),
    db.Column('user_card_id', db.Integer, db.ForeignKey('user_card.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    cards = relationship('UserCard', back_populates='user')
    decks = relationship('UserDeck', back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_decks(self, type=None):
        #TODO: unify deck types, better query
        if type is not None:
            decks = [
                d for d in self.decks
                if d.deck is not None
                and d.deck.type == type
            ]
        else:
            decks = self.decks
        return decks


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class UserCard(db.Model):
    __tablename__ = 'user_card'
    id = db.Column(db.Integer, primary_key=True)
    ease = db.Column(db.Integer, default=1)
    last_time = db.Column(db.DateTime, default=None)
    priority = db.Column(db.Boolean, default=False)
    learning = db.Column(db.Boolean, default=False)  # for reprioritisation
    sorted = db.Column(db.Boolean, default=False)
    to_study = db.Column(db.Boolean, default=True)

    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    card = db.relationship(
        'Card',
        foreign_keys=[card_id],
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship(
        'User',
        back_populates='cards'
    )

    def __repr__(self):
        return '<UserCard "{}">'.format(self.card.get_questions()[0])

    def get_dict(self):
        return {
            'id': self.id,
            # 'questions': self.card.get_questions(),
            # 'answers': self.card.get_answers()
        }

    def known(self, multiplier):
        self.ease *= multiplier
        if self.priority is True:
            self.priority = False
        else:
            self.learning = False
        self.last_time = datetime.now()

    def unknown(self, multiplier):
        ease = self.ease / multiplier
        if ease > 1:
            self.ease = math.floor(ease)
        else:
            self.ease = 1
        self.priority = True
        self.last_time = datetime.now()

    def get_questions(self):
        return self.card.get_questions()

    def get_answers(self):
        return self.card.get_answers()


class UserDeck(db.Model):
    __tablename__ = 'user_deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    card_number = db.Column(db.Integer, default=20)  # old/init cards per go
    new_card_number = db.Column(db.Integer, default=10)  # new cards per go
    card_counter = db.Column(db.Integer, default=0)
    multiplier = db.Column(db.Integer, default=2)  # ease multiplier
    entry_interval = db.Column(db.Integer, default=5)  # new card entry
    last_date = db.Column(db.Date, default=None)

    cards = relationship('UserCard', secondary=association_table)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship(
        'User',
        back_populates='decks'
    )

    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    deck = relationship(
        'Deck',
        foreign_keys=[deck_id],
    )

    type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'user_deck',
        'polymorphic_on': type
    }

    def card_total(self):
        return len(self.cards)

    def populate(self, deck):
        self.deck = deck
        self.name = deck.name
        for c in deck.cards:
            self.cards.append(
                UserCard(card=c)
            )
        db.session.add(deck)
        db.session.add(self)
        db.session.commit()

    def organise_cards(self):
        self.seen_cards = [c for c in self.cards if c.last_time is not None]
        self.unseen_cards = [c for c in self.cards if c.last_time is None]
        self.learning_cards = [c for c in self.cards if c.learning]

    def shuffle(self):
        self.organise_cards()
        if len(self.seen_cards) == 0:
            for c in self.unseen_cards[0:self.card_number]:
                c.learning = True
            db.session.commit()
            return

        min_time = min(self.seen_cards, key=lambda c: c.last_time).last_time
        delta_cards = defaultdict(list)
        for c in self.seen_cards:
            if c.to_study:
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
            if len(delta_cards) == 0:
                break

        counter = 0
        for c in self.unseen_cards:
            if c.to_study:
                c.learning = True
                counter += 1
                if counter == self.new_card_number:
                    break

        db.session.commit()

    def get_learning_cards(self):
        if len([c for c in self.cards if c.learning]) == 0:
            self.shuffle()
        return [c for c in self.cards if c.learning]

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
            card = UserCard.query.get(card_id)
            result = outcome_row.get('result')
            if result == 'z':
                card.known(self.multiplier)
            elif result == 'x':
                card.unknown(self.multiplier)
        db.session.commit()

    def process_sort(self, outcomes):
        for i in range(0, len(outcomes) - 1):
            outcome_row = outcomes[str(i+1)]
            card_id = int(outcome_row.get('id'))
            card = UserCard.query.get(card_id)
            result = outcome_row.get('result')
            if result == 'z':
                card.to_study = False
            elif result == 'x':
                card.to_study = True
            card.sorted = True
        db.session.commit()

    def get_unsorted_cards(self):
        return [c for c in self.cards if not c.sorted]

    def get_flash_cards(self, sorting=False):
        flash_cards = []
        if sorting is False:
            deck_cards = self.get_learning_cards()
        else:
            deck_cards = self.get_unsorted_cards()
        i = 0
        for c in deck_cards:
            tc = c.get_dict()
            tc['i'] = i
            tc['ease'] = c.ease
            i += 1
            flash_cards.append(tc)

        return flash_cards

    def get_display_cards(self):
        cards = defaultdict(list)
        for c in self.cards:
            if c.to_study:
                cards[1].append(c)
            else:
                cards[2].append(c)
        return cards

    def seen_total(self):
        to_study = [c for c in self.cards if c.to_study]
        return len([c for c in to_study if c.last_time])

    def to_study_total(self):
        return len([c for c in self.cards if c.to_study])


class CustomDeck(UserDeck):
    __tablename__ = 'custom_deck'
    id = db.Column(db.Integer, db.ForeignKey('user_deck.id'), primary_key=True)
    language = db.Column(db.String(32))

    __mapper_args__ = {
        'polymorphic_identity': 'custom_deck',
    }


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(50))
    frequency = db.Column(db.Integer)

    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    deck = relationship(
        'Deck',
        back_populates='cards'
    )

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


class Word(Card):
    __tablename__ = 'word'
    id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'word',
    }

    @abc.abstractmethod
    def get_questions(self):
        return

    @abc.abstractmethod
    def get_answers(self):
        return


class Character(Card):
    __tablename__ = 'character'
    id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    zi_simp = db.Column(db.String(2), index=True)
    zi_trad = db.Column(db.String(2), index=True)
    pinyin_number = db.Column(db.String(10), index=True)
    pinyin_tone = db.Column(db.String(10), index=True)
    english = db.Column(db.String(160))
    hsk = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'character',
    }

    def get_questions(self):
        q = (
            self.zi_simp,
            self.zi_trad
        )
        return q

    def get_answers(self):
        pinyin = self.pinyin_tone if self.pinyin_tone else self.pinyin_number
        a = (
            pinyin,
            self.english
        )
        return a


class Sentence(Card):
    __tablename__ = 'sentence'
    id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    zi_simp = db.Column(db.String(256), index=True)
    zi_trad = db.Column(db.String(256), index=True)
    pinyin_number = db.Column(db.String(512), index=True)
    pinyin_tone = db.Column(db.String(512), index=True)
    english = db.Column(db.String(512))
    hsk = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'sentence',
    }

    def get_questions(self):
        q = (
            self.zi_simp,
            self.zi_trad
        )
        return q

    def get_answers(self):
        pinyin = self.pinyin_tone if self.pinyin_tone else self.pinyin_number
        a = (
            pinyin,
            self.english
        )
        return a


class ArticleWord(Card):
    __tablename__ = 'article_word'
    id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'))

    word = db.relationship(
        'Word',
        foreign_keys=[word_id],
    )

    __mapper_args__ = {
        'polymorphic_identity': 'article_word',
    }

    def get_questions(self):
        return self.word.get_questions()

    def get_answers(self):
        return self.word.get_answers()


class EuropeanWord(Word):
    __tablename__ = 'european_word'
    id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    language = db.Column(db.String(32))
    word = db.Column(db.String(128))
    english = db.Column(db.String(128))

    def __repr__(self):
        return '<{}>'.format(self.word)

    __mapper_args__ = {
        'polymorphic_identity': 'european_word',
    }

    def get_questions(self):
        return self.word,

    def get_answers(self):
        if self.english is None:
            return 'WTF',
        return tuple(
            a for a in
            self.english.split('::')
        )


class ChineseWord(Word):
    __tablename__ = 'chinese_word'
    id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    zi_simp = db.Column(db.String(12), index=True)
    zi_trad = db.Column(db.String(12), index=True)
    pinyin_number = db.Column(db.String(80), index=True)
    pinyin_tone = db.Column(db.String(80), index=True)
    english = db.Column(db.String(160))
    hsk = db.Column(db.Integer)

    def __repr__(self):
        return '<{}>'.format(self.zi_simp)

    __mapper_args__ = {
        'polymorphic_identity': 'chinese_word',
    }

    def get_questions(self):
        q = (
            self.zi_simp,
            self.zi_trad
        )
        return q

    def get_answers(self):
        pinyin = self.pinyin_tone if self.pinyin_tone else self.pinyin_number
        a = (
            pinyin,
            self.english
        )
        return a


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    name = db.Column(db.String(50))

    cards = relationship('Card', back_populates='deck')

    __mapper_args__ = {
        'polymorphic_identity': 'deck',
        'polymorphic_on': type
    }

    def __repr__(self):
        return '<Deck "{}">'.format(self.name)

    @classmethod
    def get_all_json(cls, type=None):
        if type is None:
            type = cls.type
        decks = db.session.query(cls).filter_by(type=type)
        decks_json = {}
        for d in decks:
            if d.language in decks_json:
                decks_json[d.language].append(d)
            else:
                decks_json[d.language] = [d]
        return decks_json

    def card_total(self):
        return len(self.cards)


class LanguageDeck(Deck):
    __tablename__ = 'language_deck'
    id = db.Column(db.Integer, db.ForeignKey('deck.id'), primary_key=True)
    language = db.Column(db.String(32))

    __mapper_args__ = {
        'polymorphic_identity': 'language_deck',
    }


class ArticleDeck(LanguageDeck):
    __tablename__ = 'article_deck'
    id = db.Column(
        db.Integer,
        db.ForeignKey('language_deck.id'),
        primary_key=True
    )
    url = db.Column(db.String(512))
    title = db.Column(db.String(64))
    counted = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'article_deck',
    }


class ClipDeck(LanguageDeck):
    __tablename__ = 'clip_deck'
    id = db.Column(
        db.Integer,
        db.ForeignKey('language_deck.id'),
        primary_key=True
    )
    title = db.Column(db.String(128))
    text = db.Column(db.Text())

    __mapper_args__ = {
        'polymorphic_identity': 'clip_deck',
    }
