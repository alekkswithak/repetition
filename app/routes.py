from flask import (
    render_template,
    redirect,
    url_for,
    request
)
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from app import app, db
from app.forms import (
    URLForm,
    DeckSettingsForm,
    LoginForm
)
from app.models import (
    Deck,
    UserDeck,
    User,
)
from app.helpers import get_scraper


@app.route('/flash/<int:deck_id>')
def flash(deck_id):
    deck = UserDeck.query.get(deck_id)
    cards = deck.get_flash_cards()
    redirect_url = url_for('process_game')

    return render_template(
        'flash.html',
        cards=cards,
        deck_id=deck.id,
        exit_integer=len(cards),
        redirect_url=redirect_url
    )


@app.route('/sort/<int:deck_id>')
def sort(deck_id):
    deck = UserDeck.query.get(deck_id)
    cards = deck.get_flash_cards(sorting=True)
    redirect_url = url_for('process_sort')

    return render_template(
        'flash.html',
        cards=cards,
        deck_id=deck.id,
        exit_integer=len(cards),
        redirect_url=redirect_url
    )


@app.route('/process_sort', methods=['POST'])
def process_sort():
    received = request.json
    deck_id = int(received['deck_id'])
    deck = UserDeck.query.get(deck_id)
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
    deck = UserDeck.query.get(deck_id)
    deck.play_outcomes(received)
    return redirect(url_for('flash', deck_id=deck_id))


@app.route('/')
@app.route('/decks')
def decks():
    user = {'username': '学生'}
    decks = UserDeck.get_all_json(type='language_deck')
    return render_template(
        'decks.html',
        title='Home',
        user=user,
        language_decks=decks
    )


@app.route('/articles', methods=['GET', 'POST'])
def articles():
    #  user = {'username': '学生'}
    form = URLForm()
    url = ''
    if form.validate_on_submit():
        url = form.url.data
        scraper = get_scraper(url)
        ud = UserDeck()
        ud.populate(
            scraper.process_page().create_article()
        )
    return render_template(
        'articles.html',
        title='Articles',
        form=form,
        url=url,
        language_decks=UserDeck.get_all_json(
            type='article_deck'
        )
    )


@app.route('/deck/<int:deck_id>')
def browse_deck(deck_id):
    deck = Deck.query.get(deck_id)
    return render_template('browse_deck.html', deck=deck)


@app.route('/deck_settings/<int:deck_id>', methods=['GET', 'POST'])
def deck_settings(deck_id):
    form = DeckSettingsForm()
    deck = Deck.query.get(deck_id)
    if form.validate_on_submit():
        #  TODO: deck method
        #  deck.update_settings(form)
        deck.name = form.name.data
        deck.card_number = form.card_number.data
        deck.new_card_number = form.new_card_number.data
        deck.multiplier = form.multiplier.data
        deck.entry_interval = form.entry_interval.data
        db.session.commit()

    #  TODO: form method
    form.name.data = deck.name
    form.card_number.data = deck.card_number
    form.new_card_number.data = deck.new_card_number
    form.multiplier.data = deck.multiplier
    form.entry_interval.data = deck.entry_interval

    return render_template('deck_settings.html', deck=deck, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('decks'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # name conflict: flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('decks'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('decks'))
