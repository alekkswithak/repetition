from app.scraper.scraper import (
    ChineseScraper,
    EuropeanScraper,
)


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
