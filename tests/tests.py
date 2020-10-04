from datetime import datetime
import unittest
from app import app, db
from app.models import (
    Card,
    LanguageDeck
)
from queue import PriorityQueue
from .helpers import make_test_deck, make_chinese_decks


class LanguageDeckTests(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_decks_json(self):
        make_chinese_decks()
        json = LanguageDeck.get_all_json()
        self.assertIn('Chinese', json)
        self.assertEqual(len(json['Chinese']), 6)


class DeckTests(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_pq(self):
        pq = PriorityQueue()
        pq.put((1, 'one'))
        pq.put((1.1, 'two'))
        out = pq.get()
        self.assertEqual(out[1], 'one')

    def test_deck_organise_cards(self):
        deck = make_test_deck()
        deck.organise_cards()
        self.assertEqual(len(deck.seen_cards), 0)
        self.assertEqual(len(deck.unseen_cards), 52)
        self.assertEqual(len(deck.learning_cards), 0)

    def test_deck_first_shuffle(self):
        deck = make_test_deck()
        deck.shuffle()
        deck.organise_cards()
        self.assertEqual(len(deck.seen_cards), 0)
        self.assertEqual(len(deck.unseen_cards), 52)
        self.assertEqual(len(deck.learning_cards), 20)

    def test_deck_first_shuffle_organise_seen(self):
        deck = make_test_deck()
        deck.shuffle()
        deck.organise_cards()
        for c in deck.learning_cards:
            c.last_time = datetime.now()
        deck.organise_cards()
        self.assertEqual(len(deck.seen_cards), 20)
        self.assertEqual(len(deck.unseen_cards), 32)
        self.assertEqual(len(deck.learning_cards), 20)

    def test_deck_second_shuffle_after_seen(self):
        deck = make_test_deck()
        deck.shuffle()
        deck.organise_cards()
        for c in deck.learning_cards:
            c.last_time = datetime.now()
        deck.shuffle()
        deck.organise_cards()
        self.assertEqual(len(deck.seen_cards), 20)
        self.assertEqual(len(deck.unseen_cards), 32)
        self.assertEqual(len(deck.learning_cards), 30)

    def test_deck_get_learning_cards_initial(self):
        deck = make_test_deck()
        learning_cards = deck.get_learning_cards()
        self.assertEqual(len(learning_cards), 20)

    def test_deck_play_first_card_known(self):
        deck = make_test_deck()
        learning_card = deck.get_learning_cards()[0]
        outcomes = {
            '1': {'id': str(learning_card.id), 'result': 'z'},
            'non_card_data': True,
        }
        deck.play_outcomes(outcomes)
        deck.organise_cards()
        self.assertEqual(len(deck.get_learning_cards()), 19)

    def test_deck_play_first_card_unknown(self):
        deck = make_test_deck()
        learning_card = deck.get_learning_cards()[0]
        outcomes = {
            '1': {'id': str(learning_card.id), 'result': 'x'},
            'non_card_data': True,
        }
        deck.play_outcomes(outcomes)
        deck.organise_cards()
        self.assertEqual(len(deck.get_learning_cards()), 20)

    def test_deck_play_first_20_known(self):
        deck = make_test_deck()
        learning_cards = deck.get_learning_cards()
        outcomes = {'non_card_data': True}
        i = 0
        for learning_card in learning_cards:
            i += 1
            outcomes[str(i)] = {'id': str(learning_card.id), 'result': 'z'}
        deck.play_outcomes(outcomes)
        eases = [card.ease for card in deck.get_learning_cards()]
        self.assertEqual(len([e for e in eases if e == 2]), 20)
        self.assertEqual(len(deck.get_learning_cards()), 30)


if __name__ == '__main__':
    unittest.main()
