from app.scraper.scraper import (
    Scraper,
    ChineseScraper,
    EuropeanScraper
)
from app.models import ChineseWord
from app import db, app
from procs import read_hsk, read_chinese_dictionary
from collections import defaultdict, Counter
import unittest


class ScraperTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_url_language(self):
        scraper = Scraper('https://de.wikipedia.org/wiki/Spaced_repetition')
        self.assertEqual(scraper.url_language, 'german')


class GermanScraperTests(ScraperTest):

    def test_process_page(self):
        url = 'https://de.wikipedia.org/wiki/Spaced_repetition'
        scraper = EuropeanScraper(url)
        scraper.process_page()
        self.assertEqual(scraper.title, 'Spaced repetition')
        self.assertTrue(scraper.words)


class SpanishScraperTests(ScraperTest):

    def test_process_page(self):
        url = 'https://es.wikipedia.org/wiki/Repaso_espaciado'
        scraper = EuropeanScraper(url)
        scraper.process_page()
        self.assertEqual(scraper.title, 'Repaso espaciado')
        self.assertTrue(scraper.words)

    def test_create_article(self):
        url = 'https://es.wikipedia.org/wiki/Repaso_espaciado'
        scraper = EuropeanScraper(url)
        article = scraper.process_page().create_article()
        print(article)
        self.assertEqual(len(article.cards), 173)


class ChineseScraperTests(ScraperTest):

    def test_process_page(self):
        url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
        scraper = ChineseScraper(url)
        scraper.process_page()
        self.assertEqual(scraper.title, '间隔重复')
        self.assertTrue(scraper.words)

    def test_create_article(self):
        #  read_chinese_dictionary()
        url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
        scraper = ChineseScraper(url)
        article = scraper.process_page().create_article()
        print(article)
        self.assertEqual(len(article.cards), 221)

    def test_scraper_sub_words(self):
        url = 'test'
        scraper = ChineseScraper(url)
        scraper.words = Counter(['目标语言'])
        article = scraper.create_article()
        self.assertEqual(len(article.cards), 4)

    def test_scraped_words(self):
        url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
        scraper = ChineseScraper(url)
        scraper.process_page()
        found = []
        not_found = []
        read_hsk()
        #  print(len([w for w in Word.query.all() if w.hsk]))
        existing_words = {
            w.zi_simp: w for w in
            [w for w in ChineseWord.query.all() if w.hsk]
        }
        for word_text, freq in scraper.words.items():
            if word_text in existing_words:
                found.append(word_text)
            else:
                not_found.append(word_text)
        #  print(not_found)
        ew = [w for w, i in existing_words.items()]
        out = defaultdict(list)
        for w in ew:
            for n in not_found:
                if n in w or w in n:
                    out[n].append(w)
        #  print(out)
        #  breakpoint()
        self.assertEqual(len(found), 100)


if __name__ == '__main__':
    unittest.main()
