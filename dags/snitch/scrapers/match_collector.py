import logging
import os
import scrapy
import yaml
from time import sleep

# for remote run
from snitch.utils import check_for_favorite


# for local run
# from dags.snitch.utils import check_for_favorite


class MatchCollector(scrapy.Spider):
    name = 'match_collector'
    start_urls = [
        'http://www.flashscore.mobi/?d=1&s=5'  # the next day page with odds
    ]
    base_link = 'https://www.flashscore.com'

    allowed_leagues = ['ARGENTINA: Liga Profesional', 'ARGENTINA: Copa Argentina', 'AUSTRALIA: A-League',
                       'AUSTRIA: Bundesliga', 'BELGIUM: Jupiler Pro League', 'BRAZIL: Serie A',
                       'BRAZIL: Copa do Brasil', 'BULGARIA: Parva liga', 'CHINA: Super League', 'CROATIA: HNL',
                       'CZECH REPUBLIC: 1. Liga', 'DENMARK: Superliga', 'ENGLAND: Premier League',
                       'ENGLAND: Championship', 'ENGLAND: EFL Cup', 'ESTONIA: Meistriliiga', 'FRANCE: Ligue 1',
                       'GERMANY: Bundesliga', 'GERMANY: 2. Bundesliga', 'GERMANY: DFB Pokal', 'GREECE: Super League',
                       'ITALY: Serie A', 'ITALY: Serie B', 'ITALY: Coppa Italia', 'JAPAN: J1 League',
                       'NETHERLANDS: Eredivisie', 'NETHERLANDS: Eerste Divisie', 'NORWAY: Eliteserien',
                       'POLAND: Ekstraklasa', 'PORTUGAL: Liga Portugal', 'ROMANIA: Liga 1', 'RUSSIA: Premier League',
                       'SCOTLAND: Premiership', 'SCOTLAND: League Cup', 'SERBIA: Super Liga', 'SLOVENIA: Prva liga',
                       'SOUTH KOREA: K League 1', 'SPAIN: LaLiga', 'SPAIN: LaLiga2', 'SWEDEN: Allsvenskan',
                       'SWITZERLAND: Super League', 'SWITZERLAND: Swiss Cup', 'TURKEY: Super Lig', 'TURKEY: 1. Lig',
                       'TURKEY: Turkish Cup', 'UKRAINE: Premier League', 'UNITED ARAB EMIRATES: UAE League',
                       'URUGUAY: Primera Division', 'USA: MLS', 'ASIA: AFC Champions League', 'EUROPE: Euro',
                       'EUROPE: Champions League', 'EUROPE: Europa League', 'EUROPE: Europa Conference League',
                       'EUROPE: UEFA Nations League', 'EUROPE: UEFA Super Cup', 'EUROPE: Euro Women',
                       'SOUTH AMERICA: Copa Libertadores', 'SOUTH AMERICA: Copa Sudamericana', 'WORLD: World Cup']

    match_dict = dict()

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # for local run
    # file_path = '/home/lyk/PyCharmProjects/test_proj/dags'
    # matches_filename = 'data.yml'

    # for remote run
    file_path = 'vars'
    matches_filename = 'data.yml'

    def parse(self, response):
        leagues_on_page = response.xpath('//div[@id="score-data"]/h4/text()').extract()
        for ind, league_name in enumerate(leagues_on_page):
            if league_name in self.allowed_leagues:
                position = int(
                    float(response.xpath(
                        f'count(//h4[text()="{league_name}"]/preceding-sibling::h4) + 1').extract_first()))
                match_names = response.xpath(f'//text()[count(preceding-sibling::h4) = {position}]').extract()
                match_statuses = response.xpath(
                    f'//a[count(preceding-sibling::h4) = {position}]/@class').extract()  # fin - postponed, sched - scheduled
                match_part_links = response.xpath(f'//a[count(preceding-sibling::h4) = {position}]/@href').extract()
                matches_time = response.xpath(
                    f'//span[count(preceding-sibling::h4) = {position} and not(contains(@class, "odds"))]/text()').extract()

                for i, status in enumerate(match_statuses):
                    if status.lower() != 'fin':
                        match_name = match_names[i].strip()
                        match_part_link = match_part_links[i]
                        match_time = matches_time[i]
                        match_id = match_part_links[i].split('/')[-2]
                        self.match_dict[match_id] = dict()
                        self.match_dict[match_id]['league_name'] = league_name
                        self.match_dict[match_id]['time'] = match_time
                        self.match_dict[match_id]['name'] = match_name
                        self.match_dict[match_id]['link'] = f"{self.base_link}{match_part_link}"
        sorted_match_dict = {k: v for k, v in sorted(self.match_dict.items(), key=lambda item: item[1]['time'])}
        logging.info(os.listdir())

        try:
            logging.info(os.listdir('vars'))
        except Exception as e:
            logging.info(e)

        with open(f"{self.file_path}/{self.matches_filename}", 'w') as outfile:
            yaml.dump(sorted_match_dict, outfile, default_flow_style=False)
        logging.info('Sleeping for 2 secs...')
        sleep(2)
        return sorted_match_dict
