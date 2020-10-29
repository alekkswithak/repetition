from datetime import datetime
import unittest
from app import app, db
from app.models import (
    Card,
    LanguageDeck,
    UserDeck,
    ClipDeck,
)
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


class ClipDeckTests(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_deck_text(self):
        deck = ClipDeck()

