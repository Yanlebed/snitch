import logging
import os
import yaml

from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from time import sleep

from googleapiclient.discovery import build
from google.oauth2 import service_account

from snitch.main import DEFAULT_HEADERS
from snitch.scrapers.match_collector import MatchCollector
from snitch.scrapers.details_collector import DetailsCollector
from snitch.scrapers.odds_collector import OddsCollector


class MatchCollectorOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "match_collector_task"
        super(MatchCollectorOperator, self).__init__(
            python_callable=self.run_collector,
            *args,
            **kwargs)

    @staticmethod
    def run_collector():
        process = CrawlerProcess(DEFAULT_HEADERS)
        process.crawl(MatchCollector)
        process.start()


class DetailsCollectorOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "details_collector_task"
        super(DetailsCollectorOperator, self).__init__(
            python_callable=self.run_collector,
            *args,
            **kwargs)

    @staticmethod
    def run_collector():
        details = DetailsCollector(match_id=None)
        details.parse()


class OddsCollectorOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "odds_collector_task"
        super(OddsCollectorOperator, self).__init__(
            python_callable=self.retrieve_odds,
            *args,
            **kwargs)

    @staticmethod
    def retrieve_odds():
        process = CrawlerProcess(DEFAULT_HEADERS)
        process.crawl(OddsCollector)
        process.start()


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
        file_path = 'vars'
        output_file_name = 'final_data.yml'
        message_template = "Match: {teams}\n{link}\n Odds: {odds_team_1} - {odds_team_2}\n"
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
                    odds_team_2=match_data.get('t2')
                )
                bot.send_message(chat_id=chat_id, text=message_to_send)


class SheetEditorOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "odds_collector_task"
        super(SheetEditorOperator, self).__init__(
            python_callable=self.edit_sheet,
            *args,
            **kwargs)

    @staticmethod
    def edit_sheet():
        # https://www.youtube.com/watch?v=4ssigWmExak
        file_path = 'dags/snitch'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = f'{file_path}/keys.json'
        logging.info(os.listdir())

        creds = None
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # here enter the id of your sheet
        SAMPLE_SPREADSHEET_ID_input = '1iGYmQJkirhmfW0NW13_xd51pVmxk7iBH27dDLI_syds'
        SAMPLE_RANGE_NAME = 'A2:H1000'
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                          range=SAMPLE_RANGE_NAME).execute()

        values_input = result_input.get('values', [])

        logging.info(values_input)

        general_list_to_write = []
        matches_path = "vars/final_data.yml"
        logging.info('Opening matches file at {}'.format(matches_path))

        todays_date = datetime.today().strftime('%d-%m-%Y')

        with open(matches_path, 'r') as file_to_read:
            matches_dict = yaml.safe_load(file_to_read)
            logging.info(matches_dict)
            for match_id, match_data in matches_dict.items():
                general_list_to_write.append(
                    [
                        match_id,
                        todays_date,
                        match_data.get('time', 'N/A'),
                        match_data.get('league_name', 'N/A'),
                        match_data.get('name', 'N/A'),
                        match_data.get('link', 'N/A'),
                        match_data.get('t1', 'N/A'),
                        match_data.get('t2', 'N/A'),
                        match_data.get('fav', 'N/A'),
                    ]
                )


        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update
        # request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID_input, range=SAMPLE_RANGE_NAME,
        #                                 valueInputOption="USER_ENTERED", body={'values': general_list_to_write})

        append_request = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID_input, range=SAMPLE_RANGE_NAME,
                                        valueInputOption="USER_ENTERED", body={'values': general_list_to_write})

        response = append_request.execute()
        logging.info(response)


        #TODO: separate write/update methods in operator; get to result in writing/editing matches to spreadsheet
        #TODO: consider separate dag for checking schedule row in the spreadsheet