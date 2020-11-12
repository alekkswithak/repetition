import os
from app.helpers import get_chinese
from app.scraper.scraper import Scraper, ChineseScraper
from app.scraper.wiktionary_scraper import WScraper
from app.models import db
from app.models import (
    ChineseWord,
    EuropeanWord,
    Card,
    Deck,
    LanguageDeck,
    UserDeck,
    ArticleDeck,
    Sentence
)
from app.helpers import DeckMaker


def read_wiktionary(language):
    word_english = WScraper().scrape_language_to_english(language)
    for g, e in word_english.items():
        db.session.add(EuropeanWord(
            language=language,
            word=g.strip(),
            english=('::').join(e)
        ))
    db.session.commit()


def read_wiktionary_older(language):
    word_english = WScraper().scrape_english_to_language(language)
    for g, e in word_english.items():
        for w in g.split(','):
            db.session.add(EuropeanWord(
                language=language,
                word=w.strip(),
                english=('::').join(e)
            ))
    db.session.commit()


def read_chinese_dictionary():
    location = os.path.join(os.getcwd(), 'files')
    with open(
        os.path.join(location, 'cedict.txt'),
        errors='ignore',
        encoding='utf-8'
    ) as f:
        raw = f.read()
        lines = raw.split('\n')
        structures = set(len(l.split('\t')) for l in lines)
        assert len(structures) == 1
        for l in lines:
            chinese_data = l.split(' ')
            trad = chinese_data[0]
            simp = chinese_data[1]
            pinyin = l.split('[')[1].split(']')[0]
            english = l.split('/')[1]
            fields = {
                'zi_simp': simp,
                'zi_trad': trad,
                'pinyin_number': pinyin,
                'english': english,
            }
            if 'variant of' not in english:
                w = ChineseWord(**fields)
                db.session.add(w)
    db.session.commit()


def read_all_euro():
    read_wiktionary('german')
    read_wiktionary('spanish')


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
                w = ChineseWord(**fields)
                db.session.add(w)
    db.session.commit()


def read_chinese_sentences():
    """
    Reads sentences from txt and creates Sentence objects
    """
    location = os.path.join(os.getcwd(), 'files')
    with open(os.path.join(location, 'sentences.txt'), encoding='utf-8') as f:
        raw = f.read()
        lines = raw.split('\n')
        structures = set(len(l.split('\t')) for l in lines)
        assert len(structures) == 1
        for l in lines:
            data = l.split('\t')
            fields = {
                'zi_simp': get_chinese(data[0]),
                'pinyin_tone': data[1],
                'english': data[2],
            }
            s = Sentence(**fields)
            db.session.add(s)
    db.session.commit()


def read_all_chinese():
    read_chinese_dictionary()
    read_hsk()
    read_chinese_sentences()


def make_decks():
    words = Card.query.filter_by(type='word')
    decks = {n: Deck(name='HSK{}'.format(n)) for n in range(1, 7)}

    for w in words:
        decks[w.hsk].cards.append(w)
    for _, d in decks.items():
        db.session.add(d)
    db.session.commit()


def make_chinese_decks():
    words = ChineseWord.query.filter(
        ChineseWord.hsk.isnot(None)
    )
    decks = {
        n: LanguageDeck(
            name='HSK{}'.format(n),
            language='Chinese'
        )
        for n in range(1, 7)
    }
    decks['sentences'] = LanguageDeck(
        name='HSK Sentences',
        language='Chinese'
    )

    for w in words:
        decks[w.hsk].cards.append(w)

    sentences = Sentence.query.all()
    for s in sentences:
        decks['sentences'].cards.append(s)

    for _, d in decks.items():
        db.session.add(d)
    db.session.commit()

    return decks


def create_chinese_article():
    url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
    scraper = ChineseScraper(url)
    dm = DeckMaker(scraper.process_page())
    deck = dm.create_article(
        title=scraper.title,
        url=scraper.url
    )
    ud = UserDeck()
    ud.populate(deck)


def create_all():
    read_all_chinese()
    # read_all_euro()
    make_chinese_decks()
    create_chinese_article()


def read_sentences():
    location = os.path.join(os.getcwd(), 'files')

    with open(os.path.join(location, 'sentences.txt'), errors='ignore') as f:
        raw = f.read()
        lines = raw.split('\n')
        structures = set(len(l.split('\t')) for l in lines)
        assert len(structures) == 1
        for l in lines:
            pass


def count_frequency():
    ads = ArticleDeck.query.filter_by(counted=False)
    for ad in ads:
        for c in ad.cards:
            if c.word.frequency is not None:
                c.word.frequency += c.frequency
            else:
                c.word.frequency = c.frequency
        ad.counted = True
        db.session.commit()
