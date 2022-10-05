import logging
import operator
import yaml
import sys
import urllib3
import backoff

from collections import Counter
from copy import deepcopy
from lxml.html.soupparser import fromstring
from selenium import webdriver
from time import sleep

from airflow.operators.python_operator import PythonOperator

DICT_OF_DECIMAL_PARTS = {
    1: 0.25,
    2: 0.5,
    3: 0.75,
    4: 0.75,
    5: 1
}


class ExpectedCounterOperator(PythonOperator):
    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "odds_collector_task"
        super(ExpectedCounterOperator, self).__init__(
            python_callable=self.get_expected_goals,
            *args,
            **kwargs)

    @staticmethod
    def process_goals_info(goals_list):
        final_score_to_return = 0
        score_to_return = 0
        pairs_qty = 0
        for ind, goals_and_qty in enumerate(goals_list):
            if goals_and_qty[1] >= 2:
                pairs_qty += 1

        for ind, goals_and_qty in enumerate(goals_list):
            goals, qty = int(goals_and_qty[0]), goals_and_qty[1]
            if ind == 0:
                final_score_to_return = goals
                score_to_return = goals
            else:
                if goals < score_to_return:
                    final_score_to_return -= DICT_OF_DECIMAL_PARTS[qty]
                else:
                    final_score_to_return += DICT_OF_DECIMAL_PARTS[qty]

        return final_score_to_return

    def get_score(self, team_scores, team_concedes, fav):
        team_scores_counter = Counter(team_scores)
        team_concedes_counter = Counter(team_concedes)

        team_scores_counter_descending = sorted(team_scores_counter.items(), key=operator.itemgetter(1), reverse=True)
        team_concedes_counter_descending = sorted(team_concedes_counter.items(), key=operator.itemgetter(1),
                                                  reverse=True)

        teams_scores_digit = self.process_goals_info(team_scores_counter_descending)
        teams_concedes_digit = self.process_goals_info(team_concedes_counter_descending)

        return teams_scores_digit if fav else teams_concedes_digit

    def get_expected_goals(self):
        file_path = 'vars'
        output_file_name = 'final_data.yml'
        new_file_name = f'{file_path}/data_with_expected.yml'
        matches_path = f"{file_path}/{output_file_name}"
        logging.info('Opening matches file at {}'.format(matches_path))
        with open(matches_path, 'r') as file_to_read:
            with open(new_file_name, 'w') as file_to_write:
                matches_dict = yaml.safe_load(file_to_read)
                new_matches_dict = deepcopy(matches_dict)
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

                ind = 3
                for match_id, match_data in matches_dict.items():
                    if ind == 0:
                        break
                    else:
                        ind -= 1
                    # H2H, 5 last matches
                    t1_scores_goals = []
                    t1_concedes_goals = []
                    t2_scores_goals = []
                    t2_concedes_goals = []

                    req_link = f"{match_data['link']}#/h2h/overall"
                    browser.get(req_link)
                    logging.info(f"req_link: {req_link}.")
                    logging.info(f"Retrieved URL: {browser.current_url}.")
                    sleep(5)

                    tree = browser.page_source
                    h2h_blocks = fromstring(tree).xpath('//div[contains(@class, "h2h__section")]')
                    logging.info(len(h2h_blocks))
                    for ind, h2h_block in enumerate(h2h_blocks):
                        rows = h2h_block.xpath('div[@class="rows"]/div[@class="h2h__row"]')[:5]
                        if ind == 0:
                            # t1 results
                            for row in rows:
                                results = row.xpath('span[@class="h2h__result"]/span/text()')
                                home_play = row.xpath(
                                    'span[@class="h2h__homeParticipant h2h__participant highlighted"]')
                                if home_play:
                                    t1_scores_goals.append(results[0])
                                    t1_concedes_goals.append(results[1])
                                else:
                                    t1_scores_goals.append(results[1])
                                    t1_concedes_goals.append(results[0])
                        elif ind == 1:
                            # t2 results
                            for row in rows:
                                results = row.xpath('span[@class="h2h__result"]/span/text()')
                                home_play = row.xpath(
                                    'span[@class="h2h__homeParticipant h2h__participant highlighted"]')
                                if home_play:
                                    t2_scores_goals.append(results[0])
                                    t2_concedes_goals.append(results[1])
                                else:
                                    t2_scores_goals.append(results[1])
                                    t2_concedes_goals.append(results[0])
                        else:
                            logging.info(t1_scores_goals)
                            logging.info(t1_concedes_goals)
                            logging.info(t2_scores_goals)
                            logging.info(t2_concedes_goals)
                            break

                    t1_score = self.get_score(t1_scores_goals, t1_concedes_goals, match_data['fav'])
                    t2_score = self.get_score(t2_scores_goals, t2_concedes_goals, match_data['fav'])

                    logging.info(t1_score)
                    logging.info(t2_score)

                    new_matches_dict[match_id]['t1_exp_goals'] = t1_score
                    new_matches_dict[match_id]['t2_exp_goals'] = t2_score

                logging.info('Saving new_matches_dict to {}'.format(new_file_name))
                yaml.dump(new_matches_dict, file_to_write, default_flow_style=False)
