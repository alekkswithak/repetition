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
    LoginForm,
    RegistrationForm,
    ClipForm,
    CustomDeckForm,
)
from app.models import (
    Word,
    Deck,
    UserDeck,
    User,
    ArticleDeck,
    CustomDeck,
)
from app.helpers import (
    get_scraper,
    DeckMaker
)


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


@app.route('/user-decks/<int:user_id>', methods=['GET', 'POST'])
def user_decks(user_id):
    user = current_user
    form = URLForm()
    url = ''
    if form.validate_on_submit():
        url = form.url.data
        ad = ArticleDeck.query.filter_by(url=url)
        if any(a for a in ad):
            deck = ad[0]
            ud = UserDeck.query.filter_by(
                user=user,
                deck=deck
            )
            if not any(d for d in ud):
                ud = UserDeck(user=user)
                ud.populate(ad[0])
        else:
            scraper = get_scraper(url)
            dm = DeckMaker(scraper.process_page())
            deck = dm.create_article(
                title=scraper.title,
                url=scraper.url
            )
            ud = UserDeck(user=user)
            ud.populate(deck)

    decks = user.get_decks_json()
    return render_template(
        'user_decks.html',
        title='My decks',
        url=url,
        form=form,
        user=user,
        language_decks=decks
    )


@app.route('/')
@app.route('/decks')
def decks():
    user = current_user
    decks = Deck.get_all_json(type='language_deck')
    return render_template(
        'decks.html',
        title='Home',
        user=user,
        language_decks=decks
    )


@app.route('/articles', methods=['GET', 'POST'])
def articles():
    return render_template(
        'articles.html',
        title='Articles',
        user=current_user,
        language_decks=Deck.get_all_json(
            type='article_deck'
        )
    )


@app.route('/user-deck/<int:id>')
def browse_user_deck(id):
    ud = UserDeck.query.get(id)
    cards = ud.get_display_cards()
    return render_template(
        'browse_user_deck.html',
        deck=ud,
        user_cards=cards,
        user=current_user
        )


@app.route('/deck/<int:deck_id>')
def browse_deck(deck_id):
    deck = Deck.query.get(deck_id)
    if deck.type == "clip_deck":
        template = 'browse_clip_deck.html'
    else:
        template = 'browse_deck.html'
    cards = sorted(
        deck.cards,
        key=lambda w: w.frequency,
        reverse=True
    )
    user = current_user
    custom_decks = user.get_decks_json(type="custom_deck")
    return render_template(
        template,
        deck=deck,
        cards=cards,
        user=user,
        custom_decks=custom_decks,
        )


@app.route('/add-deck/<int:deck_id>')
def add_deck(deck_id):
    deck = Deck.query.get(deck_id)
    user_deck = UserDeck(user=current_user)
    user_deck.populate(deck)

    return redirect(url_for('user_decks', user_id=current_user.id))


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('decks'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/clip-decks/<int:user_id>', methods=['GET', 'POST'])
def clip_decks(user_id):
    user = current_user
    form = ClipForm()
    if form.validate_on_submit():

        title = form.title.data
        text = form.text.data
        dm = DeckMaker()
        dm.process_text(text)
        cd = dm.create_clip(
            title=title,
            text=text
        )
        ud = UserDeck(user=user)
        ud.populate(cd)

    decks = user.get_decks_json(type="clip_deck")
    return render_template(
        'clip_decks.html',
        title='Clip decks',
        form=form,
        user=user,
        language_decks=decks
    )


@app.route('/words')
def words():
    words = sorted(
        [w for w in Word.query.all() if w.frequency],
        key=lambda w: w.frequency,
        reverse=True
    )
    return render_template(
        'words.html',
        title='Words',
        cards=words,
        user=current_user,
    )


@app.route('/custom-decks/<int:user_id>', methods=['GET', 'POST'])
def custom_decks(user_id):
    user = current_user
    form = CustomDeckForm()
    if form.validate_on_submit():
        name = form.name.data
        cd = CustomDeck(name=name)
        ud = UserDeck(user=user)
        ud.populate(cd)

    decks = user.get_decks_json(type="custom_deck")
    return render_template(
        'custom_decks.html',
        title='Custom decks',
        form=form,
        user=user,
        language_decks=decks
    )
