import jieba
from app.models import ArticleDeck, Word, ArticleWord
from app import db
from lxml import html
from collections import Counter
from hanziconv import HanziConv as hc
import re
import urllib.request


def get_chinese(context):
    filter = re.compile(u'[^\u4E00-\u9FA5]') # non-Chinese unicode range
    context = filter.sub(r'', context) # remove all non-Chinese characters
    return context


class Scraper:

    def __init__(self, url):
        self.url = url
        self.title = None
        self.words = Counter()

    def process_page(self):
        page = urllib.request.urlopen(self.url)
        page_bytes = page.read()
        html_string = page_bytes.decode("utf8")
        page.close()

        tree = html.fromstring(html_string)
        self.title = tree.xpath('//h1[@class="firstHeading"]/text()')[0]
        paragraphs = tree.xpath('//div[@class="mw-parser-output"]/p/text()')

        for p in paragraphs:
            w = get_chinese(p)
            x = hc.toSimplified(w)
            self.words += Counter(jieba.cut(x, cut_all=False))

        return self

    def create_article(self):
        deck = ArticleDeck(name=self.title)
        deck.url = self.url

        existing_words = {w.zi_simp: w for w in Word.query.all()}
        #  breakpoint()
        for word_text, freq in self.words.items():
            try:
                word = existing_words[word_text]
            except KeyError:
                word = Word(zi_simp=word_text)

            article_word = ArticleWord(
                frequency=freq,
                word=word
            )
            deck.cards.append(article_word)
        db.session.add(deck)
        db.session.commit()
        return deck

