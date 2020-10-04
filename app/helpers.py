import re
from app.scraper.scraper import (
    ChineseScraper,
    EuropeanScraper,
)


def get_chinese(context):
    filter = re.compile(u'[^\u4E00-\u9FA5]')  # non-Chinese unicode range
    context = filter.sub(r'', context)  # remove all non-Chinese characters
    return context


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
