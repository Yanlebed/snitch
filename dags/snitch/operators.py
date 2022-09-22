import logging
import os
import telebot
import yaml

from airflow.operators.python_operator import PythonOperator
from scrapy.crawler import CrawlerProcess

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

    @staticmethod
    def send_matches():
        file_path = 'vars'
        output_file_name = 'final_data.yml'

        message_template = "Match: {teams}\n{link}\n Odds: {odds_team_1} - {odds_team_2}\nExpected goals: 1.1 - 2.2"
        bot_token = '5775727156:AAFji3qtTLvO4ZmFIOsLuAEsDCeM30XT7dw'
        bot_chat_id = 354467348
        bot = telebot.TeleBot(bot_token)

        matches_path = f"{file_path}/{output_file_name}"
        logging.info('Opening matches file at {}'.format(matches_path))
        with open(matches_path, 'r') as file_to_read:
            matches_dict = yaml.safe_load(file_to_read)
            logging.info(matches_dict)
            for match_id, match_data in matches_dict.items():
                logging.info('Sending message...')
                message_to_send = message_template.format(
                    teams=match_data.get('name'),
                    link=match_data.get('link'),
                    odds_team_1=match_data.get('odds_team_1'),
                    odds_team_2=match_data.get('odds_team_2')
                )
                bot.send_message(chat_id=bot_chat_id, text=message_to_send)


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
        # SAMPLE_RANGE_NAME = 'A1:AA1000'
        SAMPLE_RANGE_NAME = 'Sheet2!A1:E5'
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                          range=SAMPLE_RANGE_NAME).execute()

        values_input = result_input.get('values', [])

        logging.info(values_input)

        some_list = [[123, 'ABC'], [345, 'DEF'], [678, 'GHI']]

        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update
        request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID_input, range=SAMPLE_RANGE_NAME,
                                        valueInputOption="USER_ENTERED", body={'values': some_list})
        response = request.execute()
        logging.info(response)


        #TODO: separate write/update methods in operator; get to result in writing/editing matches to spreadsheet
        #TODO: consider separate dag for checking schedule row in the spreadsheet
        #TODO: deploy to portainer