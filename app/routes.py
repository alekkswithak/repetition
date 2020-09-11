from flask import render_template, redirect, url_for, request
from app import app
from app.models import Deck, Card


@app.route('/')
def flash():
    deck = Deck.query.filter_by(name='HSK6')[0]
    deck_cards = deck.cards[500:520]
    cards = []
    i = 0
    for c in deck_cards:
        tc = c.get_dict()
        tc['i'] = i
        i += 1
        cards.append(tc)

    return render_template('test_flash.html', cards=cards)

@app.route('/process_game', methods=['GET', 'POST'])
def process_game():
    req = request
    breakpoint()

#@app.route('/')
@app.route('/index')
def index():
    user = {'username': '学生'}
    decks = Deck.query.all()
    return render_template('decks.html', title='Home', user=user, decks=decks)


@app.route('/deck/<int:deck_id>')
def browse_deck(deck_id):
    deck = Deck.query.get(id)
    return render_template('browse_deck.html', deck=deck)


@app.route('/play_deck/<int:deck_id>')
def play_deck(deck_id):
    deck = Deck.query.get(deck_id)
    deck.play()
    card = Card.query.get(deck.active_card_id)
    return render_template('play_deck.html', card=card)


@app.route('/card_known/<int:card_id>')
def card_known(card_id):
    card = Card.query.get(card_id)
    card.known()
    return redirect(url_for('play_deck', deck_id=card.deck.id))


@app.route('/card_unknown/<int:card_id>')
def card_unknown(card_id):
    card = Card.query.get(card_id)
    card.unknown()
    return redirect(url_for('play_deck', deck_id=card.deck.id))


@app.route('/deck_browse/')
def browse_cards():
    deck = Deck.query.filter_by(name='HSK6')[0]
    cards = deck.see_cards()
    return render_template('browse_card.html', cards=cards)