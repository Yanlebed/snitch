import logging
import yaml
import sys
import urllib3
import backoff

from airflow.operators.python_operator import PythonOperator
from copy import deepcopy
from lxml.html.soupparser import fromstring
from selenium import webdriver
from time import sleep


STATS = {
    'Minute': None,
    'Home': {
        'Fav': False,
        'Shots on Goal': None,
        'Shots off Goal': None,
        'Corner Kicks': None,
        'Red Cards': None,
        'Dangerous Attacks': None,
    },
    'Away': {
        'Fav': False,
        'Shots on Goal': None,
        'Shots off Goal': None,
        'Corner Kicks': None,
        'Red Cards': None,
        'Dangerous Attacks': None,
    },
}

DICT_OF_DECIMAL_PARTS = {
    1: 0.25,
    2: 0.5,
    3: 0.75,
    4: 0.75,
    5: 1
}


class InLiveOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "in_live_task"
        super(InLiveOperator, self).__init__(
            python_callable=self.parse,
            *args,
            **kwargs)

    def parse(self):
        file_path = 'vars'
        output_file_name = 'data_with_expected.yml'
        new_file_name = f'{file_path}/match_with_stats.yml'
        matches_path = f"{file_path}/{output_file_name}"
        logging.info('Opening matches file at {}'.format(matches_path))
        with open(matches_path, 'r') as file_to_read:
            with open(new_file_name, 'w') as file_to_write:
                matches_dict = yaml.safe_load(file_to_read)
                matches_dict_with_stats = deepcopy(matches_dict)
                logging.info(matches_dict)
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s %(message)s'
                )
                #
                logging.getLogger('urllib3').setLevel(logging.ERROR)
                SELENIUM_URL = "selenium:4444"

                @backoff.on_exception(
                    backoff.expo,
                    urllib3.exceptions.MaxRetryError,
                    max_tries=5,
                    jitter=None
                )
                def selenium_connect(url):
                    return webdriver.Remote(url, {'browserName': 'chrome'})

                try:
                    browser = selenium_connect(f"http://{SELENIUM_URL}/wd/hub")
                except urllib3.exceptions.MaxRetryError:
                    logging.error("Unable to connect to Selenium.")
                    sys.exit(1)

                for match_id, match_data in matches_dict.items():
                    req_link = f"{match_data['link']}#/match-summary/match-summary"
                    #browser.get(req_link)
                    browser.get('https://www.flashscore.com/match/j3hWPw96/#/match-summary/match-summary')
                    sleep(5)
                    logging.info(f"req_link: {req_link}.")
                    logging.info(f"Retrieved URL: {browser.current_url}.")

                    tree = browser.page_source
                    logging.info(tree)

                    half = int(fromstring(tree).xpath('//span[@class="fixedHeaderDuel__detailStatus"]/text()')[0])
                    match_minutes = int(fromstring(tree).xpath('//span[@class="eventTime"]/text()')[0])

                    logging.info(half)
                    logging.info(match_minutes)

                    incidents = fromstring(tree).xpath('//div[@class="smv__incident"]')
                    logging.info(len(incidents))

                    # for incident in incidents:
                    #     inc_icon = incident.xpath('div[@class="smv__incidentIcon"]')

                    # retrieve first half stats
                    browser.get(browser.current_url.replace('#/match-summary/match-summary',
                                                            '#/match-summary/match-statistics/1'))
                    sleep(3)
                    first_half_tree = browser.page_source
                    logging.info(first_half_tree)
                    stats_categories = fromstring(first_half_tree).xpath('//div[@class="stat__category"]')

                    stats = deepcopy(STATS)
                    for category in stats_categories:
                        category_name = category.xpath('div[@class="stat__categoryName"]/text()')[0]
                        if 'shots on goal' in category_name.lower():
                            stats['Home']['Shots on Goal'] = category.xpath('//div[@class="stat__homeValue"]/text()')[0]
                            stats['Away']['Shots on Goal'] = category.xpath('//div[@class="stat__awayValue"]/text()')[0]
                        elif 'shots off goal' in category_name.lower():
                            stats['Home']['Shots off Goal'] = category.xpath('//div[@class="stat__homeValue"]/text()')[0]
                            stats['Away']['Shots off Goal'] = category.xpath('//div[@class="stat__awayValue"]/text()')[0]
                        elif 'corner kicks' in category_name.lower():
                            stats['Home']['Corner Kicks'] = category.xpath('//div[@class="stat__homeValue"]/text()')[0]
                            stats['Away']['Corner Kicks'] = category.xpath('//div[@class="stat__awayValue"]/text()')[0]
                        elif 'red cards' in category_name.lower():
                            stats['Home']['Red Cards'] = category.xpath('//div[@class="stat__homeValue"]/text()')[0]
                            stats['Away']['Red Cards'] = category.xpath('//div[@class="stat__awayValue"]/text()')[0]
                        elif 'dangerous attacks' in category_name.lower():
                            stats['Home']['Dangerous Attacks'] = category.xpath('//div[@class="stat__homeValue"]/text()')[0]
                            stats['Away']['Dangerous Attacks'] = category.xpath('//div[@class="stat__awayValue"]/text()')[0]

                    matches_dict_with_stats[match_id]['first_half_stats'] = stats

                    logging.info('Saving matches_dict_with_stats to {}'.format(new_file_name))
                    logging.info(matches_dict_with_stats)
                    yaml.dump(matches_dict_with_stats, file_to_write, default_flow_style=False)
                    break
