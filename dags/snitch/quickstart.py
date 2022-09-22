import pandas as pd
from googleapiclient.discovery import build

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID_input = '1iGYmQJkirhmfW0NW13_xd51pVmxk7iBH27dDLI_syds'
# SAMPLE_RANGE_NAME = 'A1:AA1000'
SAMPLE_RANGE_NAME = 'Sheet2!A1:E5'
service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                  range=SAMPLE_RANGE_NAME).execute()

values_input = result_input.get('values', [])

some_list = [[123, 'ABC'], [345, 'DEF'], [678, 'GHI']]

request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID_input, range=SAMPLE_RANGE_NAME,
                                valueInputOption="USER_ENTERED", body={'values': some_list})
response = request.execute()

# df = pd.DataFrame(values_input[1:], columns=values_input[0])
