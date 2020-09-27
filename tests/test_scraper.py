from app.scraper.scraper import Scraper
from app.models import Word
from procs import read_hsk
from collections import defaultdict
import unittest


class ScraperTest(unittest.TestCase):

    def test_process_page(self):
        url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
        scraper = Scraper(url)
        scraper.process_page()
        self.assertEqual(scraper.title, '间隔重复')
        self.assertTrue(scraper.words)

    def test_create_article(self):
        url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
        scraper = Scraper(url)
        article = scraper.process_page().create_article()
        print(article)
        self.assertEqual(len(article.cards), 159)

    def test_scraped_words(self):
        url = 'https://zh.wikipedia.org/wiki/%E9%97%B4%E9%9A%94%E9%87%8D%E5%A4%8D'
        scraper = Scraper(url)
        scraper.process_page()
        found = []
        not_found = []
        read_hsk()
        #  print(len([w for w in Word.query.all() if w.hsk]))
        existing_words = {
            w.zi_simp: w for w in
            [w for w in Word.query.all() if w.hsk]
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

