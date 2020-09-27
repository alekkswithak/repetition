import os
import re
from app.scraper.scraper import Scraper
from app.models import db
from app.models import Word, Card, Deck


def get_chinese(context):
    filter = re.compile(u'[^\u4E00-\u9FA5]')  # non-Chinese unicode range
    context = filter.sub(r'', context)  # remove all non-Chinese characters
    return context


def read_hsk():

    location = os.path.join(os.getcwd(), 'files\\hsk_vocab')

    for x in (1, 2, 3, 4, 5, 6):
        filename = 'HSK{}.txt'.format(x)
        with open(os.path.join(location, filename), encoding='utf-8') as f:
            raw = f.read()
            lines = raw.split('\n')
            structures = set(len(l.split('\t')) for l in lines)
            assert len(structures) == 1
            for l in lines:
                data = l.split('\t')
                fields = {
                    'zi_simp': get_chinese(data[0]),
                    'zi_trad': get_chinese(data[1]),
                    'pinyin_number': data[2],
                    'pinyin_tone': data[3],
                    'english': data[4],
                    'hsk': x,
                }
                # db magic here
                w = Word(**fields)
                db.session.add(w)
    db.session.commit()


def make_decks():
    words = Card.query.filter_by(type='word')
    decks = {n: Deck(name='HSK{}'.format(n)) for n in range(1, 7)}

    for w in words:
        decks[w.hsk].cards.append(w)
    for _, d in decks.items():
        db.session.add(d)
    db.session.commit()


def create_test_article():
    url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
    scraper = Scraper(url)
    scraper.process_page().create_article()


def read_sentences():
    location = os.path.join(os.getcwd(), 'files')

    with open(os.path.join(location, 'sentences.txt'), errors='ignore') as f:
        raw = f.read()
        lines = raw.split('\n')
        structures = set(len(l.split('\t')) for l in lines)
        assert len(structures) == 1
        for l in lines:
            pass
            # db magic here
