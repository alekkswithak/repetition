from app import app, db
from app.models import Word, Card, Deck
from tests.helpers import make_test_deck

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Word': Word,
        'Card': Card,
        'Deck': Deck,
        'd': make_test_deck()
        }
