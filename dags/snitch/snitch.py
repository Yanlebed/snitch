import scrapy


class Spider(scrapy.Spider):
    start_urls = [
        # 'http://www.flashscore.mobi/?d=1&s=5' # the next day page with odds
        'http://www.flashscore.mobi/match/Yc0HrmKs/?s=2&t=match-statistics', # match
    ]
    base_link = 'http://www.flashscore.mobi'

    base_stat_link = 'http://www.flashscore.mobi/match/{}/?s=2&t=match-statistics'

    match_dict = dict()

    x_condition = 1.9

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Referer": "http://www.flashscore.mobi/match/2LzuKwvo/?t=match-statistics",
            "Upgrade-Insecure-Requests": "1"
        }
    }

    categories = {
        'Goal Attempts': [0, 0],
        'Shots on Goal': [0, 0],
        'Shots off Goal': [0, 0],
        'Attacks': [0, 0],
        'Dangerous Attacks': [0, 0],
        'Free Kicks': [0, 0],
        'Corner Kicks': [0, 0],
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.parse)

    def parse(self, response):
        for category_name, stats in self.categories.items():
            req_xpath = f'//div[@class="stat__category" and contains (div[@class="stat__categoryName"]/text(), "{category_name}")]'
            goal_attempts = response.xpath(req_xpath)
            home_value = goal_attempts.xpath('div[@class="stat__homeValue"]/text()').extract_first()
            away_value = goal_attempts.xpath('div[@class="stat__awayValue"]/text()').extract_first()
            self.categories[category_name] = home_value, away_value
        print('hey')

    # def parse(self, response):
    #     match_links = response.xpath('//a[@class="sched"]/@href').extract()
    #     odds = response.xpath('//a[@class="sched"]/following-sibling::span[@class="mobi-odds"]')
    #     for ind, odd_group in enumerate(odds):
    #         x1_odd = float(odd_group.xpath('a/text()').extract_first())
    #         x2_odd = float(odd_group.xpath('a/text()').extract()[-1])
    #         if x1_odd < self.x_condition or x2_odd < self.x_condition:
    #             req_xpath = f'//span[@class="mobi-odds"][{ind}]'
    #             match_link = response.xpath(f'{req_xpath}/preceding-sibling::a/@href').extract()[-1]
    #             match_id = match_link.split('/')[-2]
    #             match_name = response.xpath(f'{req_xpath}/preceding-sibling::text()').extract()[-1]
    #             match_time = response.xpath(f'{req_xpath}/preceding-sibling::span/text()').extract()[-1]
    #
    #             self.match_dict[match_id] = dict()
    #             self.match_dict[match_id]['link'] = f"{self.base_link}{match_link}"
    #             self.match_dict[match_id]['name'] = match_name
    #             self.match_dict[match_id]['time'] = match_time
    #             self.match_dict[match_id]['x1'] = x1_odd
    #             self.match_dict[match_id]['x2'] = x2_odd
    #     print('hey')
