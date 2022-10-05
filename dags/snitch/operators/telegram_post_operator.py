import logging
import yaml
from time import sleep

from airflow.operators.python_operator import PythonOperator


class TelegramPostOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "odds_collector_task"
        super(TelegramPostOperator, self).__init__(
            python_callable=self.send_matches,
            *args,
            **kwargs)

    def send_matches(self, bot=None, chat_id='default'):
        # h8LzH7rQ8tcdJjP
        sleep(2)
        file_path = 'vars'
        output_file_name = 'data_with_expected.yml'
        message_template = "Match: {teams}\n{link}\n Odds: {odds_team_1} - {odds_team_2}\n" \
                           "Expected goals: {t1_exp_goals} - {t2_exp_goals}"
        matches_path = f"{file_path}/{output_file_name}"
        logging.info('Opening matches file at {}'.format(matches_path))
        with open(matches_path, 'r') as file_to_read:
            matches_dict = yaml.safe_load(file_to_read)
            logging.info(matches_dict)
            for match_id, match_data in matches_dict.items():
                logging.info('Sending message...')
                sleep(0.3)
                message_to_send = message_template.format(
                    teams=match_data.get('name'),
                    link=match_data.get('link'),
                    odds_team_1=match_data.get('t1'),
                    odds_team_2=match_data.get('t2'),
                    t1_exp_goals=match_data.get('t1_exp_goals'),
                    t2_exp_goals=match_data.get('t2_exp_goals'),
                )
                bot.send_message(chat_id=chat_id, text=message_to_send)
