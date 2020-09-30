from flask import render_template, redirect, url_for, request
from app import app
from app.forms import URLForm
from app.models import (
    Deck,
    Card,
    ArticleDeck,
    LanguageDeck
)
from app.scraper.scraper import ChineseScraper, SpanishScraper


@app.route('/flash/<int:deck_id>')
def flash(deck_id):
    #deck = Deck.query.filter_by(name='HSK6')[0]
    deck = Deck.query.get(deck_id)
    deck_cards = deck.get_learning_cards()

    # TODO: turn into model method
    cards = []
    i = 0
    for c in deck_cards:
        tc = c.get_dict()
        tc['i'] = i
        tc['ease'] = c.ease
        i += 1
        cards.append(tc)

    redirect_url = url_for('process_game')

    return render_template(
        'test_flash.html',
        cards=cards,
        deck_id=deck.id,
        exit_integer=len(deck_cards),
        redirect_url=redirect_url
    )


@app.route('/sort/<int:deck_id>')
def sort(deck_id):
    deck = Deck.query.get(deck_id)
    cards = []
    i = 0
    for c in deck.get_unsorted_cards():
        tc = c.get_dict()
        tc['i'] = i
        tc['ease'] = c.ease
        i += 1
        cards.append(tc)

    redirect_url = url_for('process_sort')

    return render_template(
        'test_flash.html',
        cards=cards,
        deck_id=deck.id,
        exit_integer=len(deck.get_unsorted_cards()),
        redirect_url=redirect_url
    )


@app.route('/process_sort', methods=['POST'])
def process_sort():
    received = request.json
    deck_id = int(received['deck_id'])
    deck = Deck.query.get(deck_id)
    deck.process_sort(received)
    return redirect(url_for('flash', deck_id=deck_id))


@app.route('/process_game', methods=['POST'])
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
    deck.play_outcomes(received)
    return redirect(url_for('flash', deck_id=deck_id))


@app.route('/')
@app.route('/index')
def index():
    user = {'username': '学生'}
    decks = LanguageDeck.get_all_json()
    return render_template(
        'decks.html',
        title='Home',
        user=user,
        language_decks=decks
    )


@app.route('/articles', methods=['GET', 'POST'])
def articles():
    user = {'username': '学生'}
    form = URLForm()
    url = ''
    if form.validate_on_submit():
        url = form.url.data

        if 'zh.wikipedia.org' in url:
            scraper = ChineseScraper(url)
        elif 'es.wikipedia.org' in url:
            scraper = SpanishScraper(url)

        scraper.process_page().create_article()
    return render_template(
        'articles.html',
        title='Articles',
        form=form,
        url=url,
        language_decks=ArticleDeck.get_all_json()
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