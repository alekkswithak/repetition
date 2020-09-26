from procs import make_decks, read_hsk
from tests.helpers import make_test_deck
from app import app, db
from app.models import (
    Word,
    Card,
    Deck,
    ArticleDeck
)


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Word': Word,
        'Card': Card,
        'Deck': Deck,
        'ArticleDeck': ArticleDeck,
        }
