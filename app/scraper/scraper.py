import jieba
from nltk.tokenize.toktok import ToktokTokenizer
import string
import abc
from app.models import (
    ArticleDeck,
    ChineseWord,
    ArticleWord,
    EuropeanWord
)
from app import db
from app.scraper.wiktionary_scraper import WScraper
from lxml import html
from collections import Counter
from hanziconv import HanziConv as hc
import re
import urllib.request


def get_chinese(context):
    filter = re.compile(u'[^\u4E00-\u9FA5]')  # non-Chinese unicode range
    context = filter.sub(r'', context)  # remove all non-Chinese characters
    return context


class Scraper(WScraper):

    def __init__(self, url):
        self.url = url
        self.title = None
        self.words = Counter()

    @abc.abstractmethod
    def process_page(self):
        return

    @abc.abstractmethod
    def create_article(self):
        return

    @property
    def url_language(self):
        if 'zh.wikipedia.org' in self.url:
            return 'chinese'
        elif 'es.wikipedia.org' in self.url:
            return 'spanish'
        elif 'de.wikipedia.org' in self.url:
            return 'german'


class EuropeanScraper(Scraper):

    def process_page(self):
        page = urllib.request.urlopen(self.url)
        page_bytes = page.read()
        html_string = page_bytes.decode("utf8")
        page.close()

        tree = html.fromstring(html_string)
        self.title = tree.xpath('//h1[@class="firstHeading"]/text()')[0]
        paragraphs = tree.xpath('//div[@class="mw-parser-output"]/p/text()')
        paragraphs += tree.xpath('//div[@class="mw-parser-output"]/p/b/text()')
        paragraphs += tree.xpath('//div[@class="mw-parser-output"]/p/a/text()')

        for p in paragraphs:
            # dummy tokenizer for now
            p = ('').join([
                c for c in p
                if c not in string.punctuation
            ])
            toktok = ToktokTokenizer()
            words = toktok.tokenize(p)
            self.words += Counter([w.replace('\n', '').lower() for w in words])
        return self

    def create_article(self):
        deck = ArticleDeck(name=self.title)
        deck.url = self.url
        language = self.url_language

        existing_words = {
            w.word: w
            for w in
            EuropeanWord.query.filter_by(
                language=language
            )}
        for word_text, freq in self.words.items():
            if word_text in existing_words:
                word = existing_words[word_text]
                article_word = ArticleWord(
                    frequency=freq,
                    word=word
                )
                deck.cards.append(article_word)
            else:
                word = EuropeanWord(
                    word=word_text,
                    language=language)
                article_word = ArticleWord(
                    frequency=freq,
                    word=word
                )
                deck.cards.append(article_word)
        db.session.add(deck)
        db.session.commit()
        return deck


class ChineseScraper(Scraper):

    def process_page(self):
        page = urllib.request.urlopen(self.url)
        page_bytes = page.read()
        html_string = page_bytes.decode("utf8")
        page.close()

        tree = html.fromstring(html_string)
        self.title = tree.xpath('//h1[@class="firstHeading"]/text()')[0]
        paragraphs = tree.xpath('//div[@class="mw-parser-output"]/p/text()')
        paragraphs += tree.xpath('//div[@class="mw-parser-output"]/p/b/text()')
        paragraphs += tree.xpath('//div[@class="mw-parser-output"]/p/a/text()')

        for p in paragraphs:
            w = get_chinese(p)
            x = hc.toSimplified(w)
            self.words += Counter(jieba.cut(x, cut_all=False))

        return self

    def create_article(self):
        deck = ArticleDeck(name=self.title)
        deck.url = self.url

        existing_words = {w.zi_simp: w for w in ChineseWord.query.all()}
        for word_text, freq in self.words.items():
            if word_text in existing_words:
                word = existing_words[word_text]
                article_word = ArticleWord(
                    frequency=freq,
                    word=word
                )
                deck.cards.append(article_word)

            else:
                sub_words = jieba.cut(word_text, cut_all=True)
                for w in sub_words:
                    if w in existing_words:
                        word = existing_words[w]
                    else:
                        word = ChineseWord(zi_simp=w)

                    article_word = ArticleWord(
                        frequency=freq,
                        word=word
                    )
                    deck.cards.append(article_word)

        db.session.add(deck)
        db.session.commit()
        return deck

