from datetime import datetime
import unittest
from app import app, db
from app.models import (
    User,
    UserCard,
    UserDeck,
    Card,
)
from .helpers import make_test_deck


class UserTests(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_cards_relationship(self):
        u = User()
        c = UserCard()
        u.cards.append(c)
        self.assertEqual(len(u.cards), 1)

    def test_decks_relationship(self):
        u = User()
        d = UserDeck()
        u.decks.append(d)
        self.assertEqual(len(u.decks), 1)


class TestUserCard(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_card_relationship(self):
        uc = UserCard()
        self.assertIsNone(uc.card)
        c = Card()
        uc.card = c
        self.assertTrue(uc.card)


class UserDeckTests(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_cards_relationship(self):
        d = UserDeck()
        c = UserCard()
        d.cards.append(c)
        dd = UserDeck()
        dd.cards.append(c)
        db.session.add(d)
        db.session.add(dd)
        self.assertEqual(
            len(UserCard.query.all()), 1
        )

    def test_user_deck_populate(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        self.assertEqual(len(user_deck.cards), 52)

    def test_deck_organise_cards(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        user_deck.organise_cards()
        self.assertEqual(len(user_deck.seen_cards), 0)
        self.assertEqual(len(user_deck.unseen_cards), 52)
        self.assertEqual(len(user_deck.learning_cards), 0)

    def test_deck_first_shuffle(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        user_deck.shuffle()
        user_deck.organise_cards()
        self.assertEqual(len(user_deck.seen_cards), 0)
        self.assertEqual(len(user_deck.unseen_cards), 52)
        self.assertEqual(len(user_deck.learning_cards), 20)

    def test_deck_first_shuffle_organise_seen(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        user_deck.shuffle()
        user_deck.organise_cards()
        for c in user_deck.learning_cards:
            c.last_time = datetime.now()
        user_deck.organise_cards()
        self.assertEqual(len(user_deck.seen_cards), 20)
        self.assertEqual(len(user_deck.unseen_cards), 32)
        self.assertEqual(len(user_deck.learning_cards), 20)

    def test_deck_second_shuffle_after_seen(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        user_deck.shuffle()
        user_deck.organise_cards()
        for c in user_deck.learning_cards:
            c.last_time = datetime.now()
        user_deck.shuffle()
        user_deck.organise_cards()
        self.assertEqual(len(user_deck.seen_cards), 20)
        self.assertEqual(len(user_deck.unseen_cards), 32)
        self.assertEqual(len(user_deck.learning_cards), 30)

    def test_deck_get_learning_cards_initial(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        learning_cards = user_deck.get_learning_cards()
        self.assertEqual(len(learning_cards), 20)

    def test_deck_play_first_card_known(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        learning_card = user_deck.get_learning_cards()[0]
        outcomes = {
            '1': {'id': str(learning_card.id), 'result': 'z'},
            'non_card_data': True,
        }
        user_deck.play_outcomes(outcomes)
        user_deck.organise_cards()
        self.assertEqual(len(user_deck.get_learning_cards()), 19)

    def test_deck_play_first_card_unknown(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        learning_card = user_deck.get_learning_cards()[0]
        outcomes = {
            '1': {'id': str(learning_card.id), 'result': 'x'},
            'non_card_data': True,
        }
        user_deck.play_outcomes(outcomes)
        user_deck.organise_cards()
        self.assertEqual(len(user_deck.get_learning_cards()), 20)

    def test_deck_play_first_20_known(self):
        deck = make_test_deck()
        user_deck = UserDeck()
        user_deck.populate(deck)
        learning_cards = user_deck.get_learning_cards()
        outcomes = {'non_card_data': True}
        i = 0
        for learning_card in learning_cards:
            i += 1
            outcomes[str(i)] = {'id': str(learning_card.id), 'result': 'z'}
        user_deck.play_outcomes(outcomes)
        eases = [card.ease for card in user_deck.get_learning_cards()]
        self.assertEqual(len([e for e in eases if e == 2]), 20)
        self.assertEqual(len(user_deck.get_learning_cards()), 30)


if __name__ == '__main__':
    unittest.main()
