import os
import re
from app import app, db
from app.models import (
    Deck,
    Card,
    ChineseWord,
    LanguageDeck
)


def get_chinese(context):
    filter = re.compile(u'[^\u4E00-\u9FA5]')  # non-Chinese unicode range
    context = filter.sub(r'', context)  # remove all non-Chinese characters
    return context


def make_test_deck():

    location = os.path.join(os.getcwd(), '')
    filename = 'tests\\test_words.txt'

    with open(os.path.join(location, filename), encoding='utf-8') as f:
        raw = f.read()
        lines = raw.split('\n')
        structures = set(len(l.split('\t')) for l in lines)
        assert len(structures) == 1
        words = []
        for l in lines:
            data = l.split('\t')
            fields = {
                'zi_simp': get_chinese(data[0]),
                'zi_trad': get_chinese(data[1]),
                'pinyin_number': data[2],
                'pinyin_tone': data[3],
                'english': data[4],
                'hsk': 6,
            }
            words.append(ChineseWord(**fields))
        deck = Deck(name='Test')
        for w in words:
            db.session.add(w)
            deck.cards.append(w)
    db.session.add(deck)
    db.session.commit()
    return deck


def make_chinese_decks():
    words = Card.query.filter_by(type='chinese_word')
    decks = {
        n: LanguageDeck(
            name='HSK{}'.format(n),
            language='Chinese'
        )
        for n in range(1, 7)
    }

    for w in words:
        decks[w.hsk].cards.append(w)
    for _, d in decks.items():
        db.session.add(d)
    db.session.commit()
