from flask import render_template, redirect, url_for
from app import app
from app.models import Deck, Card


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


@app.route('/play_deck/<int:deck_id>')
def play_deck(deck_id):
    deck = Deck.query.get(deck_id)
    deck.play()
    card = Card.query.get(deck.active_card_id)
    return render_template('play_deck.html', card=card)


@app.route('/evaluate_card/<int:card_id>/<known>')
def evaluate_card(card_id, known):
    card = Card.query.get(card_id)
    print(type(known))
    print(known is False)
    if known:
        print('known')
        card.known()
    else:
        print('unknown')
        card.unknown()
    return redirect(url_for('play_deck', deck_id=card.deck.id))


@app.route('/deck_browse/')
def browse_cards():
    deck = Deck.query.filter_by(name='HSK6')[0]
    cards = deck.see_cards()
    return render_template('browse_card.html', cards=cards)