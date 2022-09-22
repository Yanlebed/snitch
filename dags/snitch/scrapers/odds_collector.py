import scrapy
import yaml

from copy import deepcopy

# for remote run
from snitch.utils import check_for_favorite


# for local run
# from dags.snitch.utils import check_for_favorite


class OddsCollector(scrapy.Spider):
    name = 'odds_collector'
    start_urls = [
        'http://www.flashscore.mobi/',
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }
    matches = dict()

    # for local run
    # file_path = '/home/lyk/PyCharmProjects/test_proj/dags'
    # source_matches_filename = 'data.yml'
    # output_file_name = 'final_data.yml'

    # for remote run
    file_path = 'vars'
    source_matches_filename = 'data.yml'
    output_file_name = 'final_data.yml'

    def start_requests(self):
        with open(f"{self.file_path}/{self.source_matches_filename}", 'r') as stream:
            self.matches = yaml.safe_load(stream)
            matches = deepcopy(self.matches)
            for match_id, match_data in matches.items():
                yield scrapy.Request(match_data.get('link'), callback=self.parse, meta={'match_id': match_id})

    def parse(self, response):
        match_id = response.meta['match_id']
        odds = response.xpath('//p[@class="p-set odds-detail"]/a/text()').extract() or ['0', '0', '0']
        odd_t1 = float(odds[0])
        odd_t2 = float(odds[2])
        fav = check_for_favorite(odd_t1, odd_t2)
        if fav:
            self.matches[match_id]['fav'] = fav
            self.matches[match_id]['t1'] = odd_t1
            self.matches[match_id]['t2'] = odd_t2
        else:
            del self.matches[match_id]

    def closed(self, reason):
        sorted_match_dict = {k: v for k, v in sorted(self.matches.items(), key=lambda item: item[1]['time'])}
        with open(f"{self.file_path}/{self.output_file_name}", 'w') as outfile:
            yaml.dump(sorted_match_dict, outfile, default_flow_style=False)
