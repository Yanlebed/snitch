from scrapy.crawler import CrawlerProcess

# for remote run
from snitch.scrapers.match_collector import MatchCollector
from snitch.scrapers.details_collector import DetailsCollector
from snitch.scrapers.odds_collector import OddsCollector
from snitch.utils import sort_matches

# for local run
# from scrapers.match_collector import MatchCollector
# from scrapers.odds_collector import OddsCollector
# from scrapers.details_collector import DetailsCollector
# from utils import sort_matches

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": "http://www.flashscore.mobi/match/2LzuKwvo/?t=match-statistics",
    "Upgrade-Insecure-Requests": "1"
}


def main():
    process = CrawlerProcess(DEFAULT_HEADERS)
    process.crawl(MatchCollector)
    process.start(stop_after_crawl=False)

    # process_2 = CrawlerProcess(DEFAULT_HEADERS)
    # process_2.crawl(OddsCollector)
    # process_2.start()

    sort_matches()
    # details = DetailsCollector(match_id=None)
    # details.parse()

if __name__ == '__main__':
    main()
