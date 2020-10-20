import re
from collections import Counter
import jieba
from hanziconv import HanziConv as hc
from app import db
from app.scraper.scraper import (
    ChineseScraper,
    EuropeanScraper,
)
from app.models import (
    ArticleDeck,
    ClipDeck,
    ChineseWord,
    ArticleWord,
)


def get_chinese(context):
    filter = re.compile(u'[^\u4E00-\u9FA5]')  # non-Chinese unicode range
    context = filter.sub(r'', context)  # remove all non-Chinese characters
    return context


class DeckMaker:

    def __init__(self, words=None):
        self.words = words

    def process_text(self, text):
        w = get_chinese(text)
        x = hc.toSimplified(w)
        self.words = Counter(jieba.cut(x, cut_all=False))

    def create_deck(self, deck):
        hsk_words = {w.zi_simp: w for w in ChineseWord.query.all() if w.hsk}
        existing_words = {w.zi_simp: w for w in ChineseWord.query.all()}
        for word_text, freq in self.words.items():
            if word_text in hsk_words:
                word = hsk_words[word_text]
            elif word_text in existing_words:
                word = existing_words[word_text]
            else:
                sub_words = jieba.cut(word_text, cut_all=True)
                for w in sub_words:
                    if w in existing_words:
                        word = existing_words[w]
                        article_word = ArticleWord(
                            frequency=freq,
                            word=word
                        )
                        deck.cards.append(article_word)
                continue

            article_word = ArticleWord(
                frequency=freq,
                word=word
            )
            deck.cards.append(article_word)

        db.session.add(deck)
        db.session.commit()
        return deck

    def create_article(self, title, url):
        deck = ArticleDeck(name=title, url=url)
        return self.create_deck(deck)

    def create_clip(self, title, text):
        deck = ClipDeck(name=title, text=text)
        return self.create_deck(deck)



def get_scraper(url):
    if 'zh.wikipedia.org' in url:
        scraper = ChineseScraper(url)
    elif any(f in url for f in (
        'es.wikipedia.org',
        'de.wikipedia.org'
        )
    ):
        scraper = EuropeanScraper(url)

    return scraper
