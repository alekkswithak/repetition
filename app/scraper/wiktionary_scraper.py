from lxml import html
import urllib.request
import random
from xml.etree import cElementTree as ET
from collections import defaultdict
import string


class WScraper:

    @property
    def urls(self):
        return {
            'german': [
                ('https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/en-de-{}').format(x)
                for x in 'abcdefghijklmnopqrstuvwxyz'
            ],
            'spanish': [
                ('https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/en-es-{}').format(x)
                for x in 'abcdefghijklmnopqrstuvwxyz'
            ]
        }

    def scrape_language(self, language):
        out = defaultdict(list)
        for url in self.urls[language]:
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
                words = german.split(',')
                english = tr.text_content().replace('\n', '').split('::')[0].strip()
                for w in words:
                    sanitised_w = w.split('{')[0].strip()
                    w = ('').join([
                        c for c in sanitised_w
                        if c not in string.punctuation+string.digits
                    ]).strip()
                    if len(w.split(' ')) == 1:
                        out[w].append(english)

            #print({k: out[k] for k in random.sample(list(out), 10)})

        return out

