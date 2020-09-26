from flask import render_template, redirect, url_for, request
from app import app
from app.forms import URLForm
from app.models import (
    Deck,
    Card,
    ArticleDeck
)
from scraper.scraper import Scraper


@app.route('/flash/<int:deck_id>')
def flash(deck_id):
    #deck = Deck.query.filter_by(name='HSK6')[0]
    deck = Deck.query.get(deck_id)
    deck_cards = deck.get_learning_cards()
    print(deck_cards)
    cards = []
    i = 0
    for c in deck_cards:
        tc = c.get_dict()
        tc['i'] = i
        tc['ease'] = c.ease
        i += 1
        cards.append(tc)

    return render_template(
        'test_flash.html',
        cards=cards,
        deck_id=deck.id,
        exit_integer=len(deck_cards)
    )


@app.route('/process_game', methods=['GET', 'POST'])
def process_game():
    """
        POST :
            {
                '1': {'id': '2516', 'result': 'x'},
                '2': {'id': '2517', 'result': 'z'},
                'deck_id': '6'
            }
    """

    received = request.json
    deck_id = int(received['deck_id'])
    deck = Deck.query.get(deck_id)
    print(received)
    #breakpoint()
    deck.play_outcomes(received)
    return redirect(url_for('flash', deck_id=deck_id))


@app.route('/')
@app.route('/index')
def index():
    user = {'username': '学生'}
    decks = Deck.query.all()
    return render_template('decks.html', title='Home', user=user, decks=decks)


@app.route('/articles', methods=['GET', 'POST'])
def articles():
    user = {'username': '学生'}
    form = URLForm()
    url = ''
    if form.validate_on_submit():
        url = form.url.data
        scraper = Scraper(url)
        scraper.process_page().create_article()
    return render_template(
        'articles.html',
        title='Articles',
        form=form,
        url=url,
        decks=ArticleDeck.query.all()
    )


@app.route('/deck/<int:deck_id>')
def browse_deck(deck_id):
    deck = Deck.query.get(id)
    return render_template('browse_deck.html', deck=deck)


@app.route('/deck_browse/')
def browse_cards():
    deck = Deck.query.filter_by(name='HSK6')[0]
    cards = deck.see_cards()
    return render_template('browse_card.html', cards=cards)