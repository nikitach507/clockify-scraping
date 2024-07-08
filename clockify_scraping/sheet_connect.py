import os
import json
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from clockify_scraping.config.settings import Settings

class GoogleSheetAPI:
    def __init__(self, spreadsheet_id: str, credentials_path: str, token_path: str) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.spreadsheet_id = spreadsheet_id
        self.gc = None
        self.credentials = None

    def authorize(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']

        if os.path.exists(self.token_path):
            with open(self.token_path, 'r') as token:
                self.credentials = Credentials.from_authorized_user_info(json.load(token), scopes)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, scopes)
                self.credentials = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(self.credentials.to_json())

        self.gc = gspread.authorize(self.credentials)

    def open_sheet(self) -> gspread.Spreadsheet:
        if not self.gc:
            self.authorize()
        return self.gc.open_by_key(self.spreadsheet_id)

    def read_data(self, sheet_name: str, range_name: str) -> list:
        try:
            worksheet = self.open_sheet().worksheet(sheet_name)
            result = worksheet.get(range_name)
            return result
        except gspread.exceptions.APIError as e:
            print(f"APIError: {e}")
            raise

    def write_data(self, sheet_name: str, range_name: str, data: list) -> None:
        try:
            worksheet = self.open_sheet().worksheet(sheet_name)
            worksheet.update(range_name, data)
        except gspread.exceptions.APIError as e:
            print(f"APIError: {e}")
            raise

    def append_data(self, sheet_name: str, data: list) -> None:
        try:
            worksheet = self.open_sheet().worksheet(sheet_name)
            worksheet.append_row(data)
        except gspread.exceptions.APIError as e:
            print(f"APIError: {e}")
            raise


if __name__ == '__main__':
    credentials_file_path = Settings.GOOGLE_SHEETS_CREDENTIALS_FILE
    token_file_path = Settings.GOOGLE_OAUTH_TOKEN_FILE
    gs = GoogleSheetAPI(credentials_path=credentials_file_path, token_path=token_file_path, spreadsheet_id=Settings.SPREADSHEET_ID)
    
    data = gs.read_data(Settings.SPREADSHEET_NAME, 'A1:B2')
    print(data)
    gs.append_data(Settings.SPREADSHEET_NAME, ['test', 'test'])
    data = gs.read_data(Settings.SPREADSHEET_NAME, 'A1:B2')
    print(data)