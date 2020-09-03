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

    # def test_deck_get_card(self):
    #     deck = make_test_deck()
    #     for c in deck.cards:
    #         c.ease = 2 if c.zi_simp != '自满' else 1
    #     card = deck.get_card()
    #     self.assertEqual(card.zi_simp, '自满')

    def test_deck_organise_cards(self):
        deck = make_test_deck()
        deck.organise_cards()
        self.assertEqual(len(deck.seen_cards), 0)
        self.assertEqual(len(deck.unseen_cards), 52)
        self.assertEqual(len(deck.learning_cards), 0)

    def test_deck_first_play(self):
        deck = make_test_deck()
        deck.play()
        self.assertEqual(deck.active_card_id, 1)
        self.assertEqual(len(deck.seen_cards), 0)
        self.assertEqual(len(deck.unseen_cards), 52)
        self.assertEqual(len(deck.learning_cards), 20)

    def test_deck_play_two(self):
        """
        Checks deck status after two cards played
        """
        deck = make_test_deck()
        outcomes = [True, True]
        play_deck(deck, outcomes)
        deck.play()
        self.assertEqual(deck.active_card_id, 3)
        self.assertEqual(len(deck.seen_cards), 2)
        self.assertEqual(len(deck.unseen_cards), 50)
        self.assertEqual(len(deck.learning_cards), 20)

    def test_deck_play_twenty_one(self):
        """
        Checks deck status after two cards played
        """
        deck = make_test_deck()
        outcomes = [True for _ in range(21)]
        play_deck(deck, outcomes)
        deck.play()
        self.assertEqual(len(deck.seen_cards), 20)
        self.assertEqual(len(deck.unseen_cards), 32)
        self.assertEqual(len(deck.learning_cards), 20)

    def test_deck_play_200_correct(self):
        """
        Checks deck status after two cards played
        """
        deck = make_test_deck()
        outcomes = [True for _ in range(200)]
        play_deck(deck, outcomes)
        deck.play()
        c = max(deck.cards, key=lambda c: c.ease)
        self.assertEqual(c.ease, 32)
        self.assertEqual(len(deck.seen_cards), 50)
        self.assertEqual(len(deck.unseen_cards), 2)
        self.assertEqual(len(deck.learning_cards), 20)

    def test_deck_play_200_incorrect(self):
        """
        Checks deck status after two cards played
        """
        deck = make_test_deck()
        outcomes = [False for _ in range(200)]
        play_deck(deck, outcomes)
        deck.play()
        c = max(deck.cards, key=lambda c: c.ease)
        self.assertEqual(c.ease, 1)
        self.assertEqual(len(deck.seen_cards), 50)
        self.assertEqual(len(deck.unseen_cards), 2)
        self.assertEqual(len(deck.learning_cards), 20)

    def test_stress_deck(self):
        deck = Deck()
        deck.cards.extend([
            Card()
            for _ in range(12000)
        ])
        print(len(deck.cards))
        db.session.add(deck)
        db.session.commit()
        outcomes = [True for _ in range(12000)]
        play_deck(deck, outcomes)
        c = max(deck.cards, key=lambda c: c.ease)
        self.assertEqual(c.ease, 1)
        self.assertEqual(len(deck.seen_cards), 50)
        self.assertEqual(len(deck.unseen_cards), 2)
        self.assertEqual(len(deck.learning_cards), 20)


def play_deck(deck, outcomes):
    """
    plays as many cards as there are in outcomes
    outcomes is a list of bool
    """
    played = []
    for out in outcomes:
        deck.play()
        card = Card.query.get(deck.active_card_id)
        if out is True:
            card.known()
        elif out is False:
            card.unknown()
        played.append(card)
        print(len(played))

    return played




if __name__ == '__main__':
    unittest.main()