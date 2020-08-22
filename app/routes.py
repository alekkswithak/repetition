from flask import render_template
from app import app
from app.models import Deck


@app.route('/')
@app.route('/index')
def index():
    user = {'username': '学生'}
    decks = Deck.query.all()
    return render_template('decks.html', title='Home', user=user, decks=decks)


@app.route('/deck/<id>')
def browse_deck(id):
    deck = Deck.query.get(id)
    return render_template('browse_deck.html', deck=deck)


@app.route('/deck_browse/')
def browse_cards():
    deck = Deck.query.filter_by(name='HSK6')[0]
    cards = deck.see_cards()
    return render_template('browse_card.html', cards=cards)
