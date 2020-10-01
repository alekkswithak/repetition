from app.scraper.scraper import (
    ChineseScraper,
    SpanishScraper,
    GermanScraper
)


def get_scraper(url):
    if 'zh.wikipedia.org' in url:
        scraper = ChineseScraper(url)
    elif 'es.wikipedia.org' in url:
        scraper = SpanishScraper(url)
    elif 'de.wikipedia.org' in url:
        scraper = GermanScraper(url)

    return scraper
