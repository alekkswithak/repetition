from app import app, db
from app.models import Word, Card, Deck
from tests.helpers import make_test_deck
from procs import make_decks, read_hsk

@app.shell_context_processor
def make_shell_context():
    if len(Deck.query.all()) == 0:
        read_hsk()
        make_decks()
    return {
        'db': db,
        'Word': Word,
        'Card': Card,
        'Deck': Deck,
        'd': Deck.query.filter_by(name='HSK6')[0]
        }
