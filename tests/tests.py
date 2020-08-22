from datetime import datetime
import unittest, os
from app import app, db
from app.models import Deck, Card, Word
from queue import PriorityQueue
from .helpers import make_test_deck

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
    
    def test_deck_get_card(self):
        deck = make_test_deck()
        for c in deck.cards:
            c.ease = 2 if c.zi_simp != '自满' else 1
        card = deck.get_card()
        self.assertEqual(card.zi_simp, '自满')
    
    def test_


if __name__ == '__main__':
    unittest.main()