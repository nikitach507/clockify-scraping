import os
import json
import gspread
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
from collections import defaultdict
    

def generate_total_rows(current_date: str, day_total: dict[str, str], found_users: dict[str, str]) -> list[list[str]]:
    total_row = [f'TOTAL [{current_date}]'] + [
        f"{int((datetime.strptime(day_total[user_id]['end_time'], '%H:%M') - datetime.strptime(day_total[user_id]['start_time'], '%H:%M')).total_seconds() / 3600 // 1)}."
        f"{int((datetime.strptime(day_total[user_id]['end_time'], '%H:%M') - datetime.strptime(day_total[user_id]['start_time'], '%H:%M')).total_seconds() / 60 % 60):02d} h."
        if 'start_time' in day_total[user_id] else '0.0 h.'
        for user_id in found_users.values()
    ]
    separator_row = ['-' * 20] * len(total_row)
    return [separator_row, total_row, separator_row]


def append_data_to_sheet(worksheet: gspread.Worksheet, data: list[list[datetime | str]], current_date: str) -> None:
    while True:
        try:
            worksheet.append_rows(data)
            break
        except gspread.exceptions.APIError as e:
            print(f"Error appending rows for date {current_date}: {e}")
            time.sleep(30)


def append_all_totals(worksheet: gspread.Worksheet, day_totals: list[dict], found_users: dict[str, str], start_date: str, stop_date: str) -> None:
    total_times = defaultdict(int)
    for day_total in day_totals:
        for user_id in found_users.values():
            if 'start_time' in day_total[user_id] and 'end_time' in day_total[user_id]:
                start_time = datetime.strptime(day_total[user_id]['start_time'], '%H:%M')
                end_time = datetime.strptime(day_total[user_id]['end_time'], '%H:%M')
                total_times[user_id] += int((end_time - start_time).total_seconds() / 60)
    all_total_row = [f'ALL TOTAL [{start_date} / {stop_date}]'] + [
        f"{total_times[user_id] // 60}.{total_times[user_id] % 60:02d} h."
        for user_id in found_users.values()
    ]
    worksheet.append_rows([all_total_row])


class GoogleSheetAPI:
    def __init__(self, spreadsheet_id: str, credentials_path: str, token_path: str) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.spreadsheet_id = spreadsheet_id
        self.gc = None
        self.credentials = None

    def _authorize(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']

        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as token:
                    self.credentials = Credentials.from_authorized_user_info(json.load(token), scopes)
        except (FileNotFoundError, TypeError) as e:
            raise e

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
            self._authorize()
        return self.gc.open_by_key(self.spreadsheet_id)
    
    def prepare_worksheet(self, sheet_name: str) -> gspread.Worksheet:
        try:
            self.open_sheet().worksheet(sheet_name)
            print(f"Sheet {sheet_name} already exists.")
            exit(0)
        except gspread.exceptions.WorksheetNotFound:
            try:
                self.open_sheet().add_worksheet(title=sheet_name, rows="1000", cols="26")
                worksheet = self.open_sheet().worksheet(sheet_name)
                print(f"Sheet {sheet_name} created.")
                return worksheet
            except gspread.exceptions.APIError as e:
                print(f"Error creating sheet {sheet_name}: {e}")
                exit(1)