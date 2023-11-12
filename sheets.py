import os
from constants import ColumnNames

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# OAuth Scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1Embun0NenkLiepVQAtmaty2Xc5jvx22zNJLVtd0hg5Y'


# create a credentials.json to access the spreadsheet
# @return: Credentials
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


# @param headers: list of strings
# @param column_name: string
# @return: int
def get_column_index(headers, column_name):
    return headers.index(column_name)


# @param column_index: int
# @return: string
def get_column_label(column_index):
    return chr(ord('A') + column_index)


def get_sheet():
    return build('sheets', 'v4', credentials=get_credentials()).spreadsheets()


# @param headers: list of strings
# @param values: list of lists of strings
# @param sheet: Google Sheet
# @param participant: Participant
def update_participants_points(headers, values, sheet, participants):
    column_label = get_column_label(
        get_column_index(headers, ColumnNames.POINTS))

    points = [[p.points] for p in participants]

    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f'Sheet1!{column_label}{2}:{column_label}{len(values)+1}',
        valueInputOption='USER_ENTERED',
        body={'values': points}
    ).execute()
