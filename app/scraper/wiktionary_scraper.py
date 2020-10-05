import string
import urllib.request
from collections import defaultdict
from lxml import html


BASE_URL = 'https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/'


class WScraper:

    def urls(self):
        return {
            'german': [
                (BASE_URL + 'de-en-{}').format(x)
                for x in 'abcdefghijklmnopqrstuvwxyz'
            ],
            'spanish': [
                (BASE_URL + 'es-en-{}').format(x)
                for x in 'abcdefghijklmnopqrstuvwxyz'
            ]
        }

    def scrape_language_to_english(self, language):
        out = defaultdict(list)
        for url in self.urls()[language]:
            page = urllib.request.urlopen(url)
            page_bytes = page.read()
            html_string = page_bytes.decode("utf8")
            page.close()
            tree = html.fromstring(html_string)
            td = tree.xpath('//div[@class="mw-parser-output"]/table/tbody/tr')

            for tr in td:
                german = tr.text_content().replace(
                    '\n', ''
                ).split('::')[0].strip()

                english = tr.text_content().replace(
                    '\n', ''
                ).split('::')[1].strip()

                sanitised_w = german.split('{')[0].strip()
                w = ('').join([
                    c for c in sanitised_w
                    if c not in string.punctuation+string.digits
                ]).strip()
                if len(w.split(' ')) == 1 and w != '':
                    out[w].append(english)

        return out

    def scrape_english_to_language(self, language):
        out = defaultdict(list)
        for url in self.urls()[language]:
            page = urllib.request.urlopen(url)
            page_bytes = page.read()
            html_string = page_bytes.decode("utf8")
            page.close()
            tree = html.fromstring(html_string)
            td = tree.xpath('//div[@class="mw-parser-output"]/table/tbody/tr')

            for tr in td:
                german = tr.text_content().replace(
                    '\n', ''
                ).split('::')[1].strip()

                english = tr.text_content().replace(
                    '\n', ''
                ).split('::')[0].strip()

                words = german.split(',')
                for w in words:
                    sanitised_w = w.split('{')[0].strip()
                    w = ('').join([
                        c for c in sanitised_w
                        if c not in string.punctuation+string.digits
                    ]).strip()
                    if len(w.split(' ')) == 1:
                        out[w].append(english)

        return out
