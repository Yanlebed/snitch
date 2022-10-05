import logging
import os
import yaml
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2 import service_account

from airflow.operators.python_operator import PythonOperator


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
        matches_path = "vars/data_with_expected.yml"
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
                        match_data.get('t1_exp_goals', 'N/A'),
                        match_data.get('t2_exp_goals', 'N/A'),
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

        # TODO: separate write/update methods in operator; get to result in writing/editing matches to spreadsheet
        # TODO: consider separate dag for checking schedule row in the spreadsheet
