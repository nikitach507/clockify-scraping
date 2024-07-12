import os
import json
import gspread
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
from collections import defaultdict
    

def generate_total_rows(current_date: str, start_row: int, found_users: dict[str, str], num_rows: int = 96) -> list[list[str]]:
    total_formula_row = []
    for col_index, user in enumerate(found_users.values(), start=1):
        column_letter = chr(ord('A') + col_index)

        count_formula = f"COUNTIF({column_letter}{start_row}:{column_letter}{start_row + num_rows - 1}, \"<>-\")"
        
        total_minutes = f"{count_formula} * 15"
        formatted_time_formula = f"=TEXT(INT({total_minutes} / 60), \"0\") & \":\" & TEXT(MOD({total_minutes}, 60), \"00\")"

        
        total_formula_row.append(formatted_time_formula)

    total_row = [f'TOTAL [{current_date}]'] + total_formula_row
    return [total_row]

def append_data_to_sheet(worksheet: gspread.Worksheet, data: list[list[datetime | str]], current_date: str, found_users: dict[str, str], start_row: int) -> None:
    while True:
        try:
            worksheet.append_rows(data, value_input_option='USER_ENTERED')
            total_rows = generate_total_rows(current_date, start_row, found_users)
            worksheet.append_rows(total_rows, value_input_option='USER_ENTERED')
            break
        except gspread.exceptions.APIError as e:
            print(f"Error appending rows for date {current_date}: {e}")
            time.sleep(30)

def append_all_totals(worksheet: gspread.Worksheet, num_days: int, found_users: dict[str, str], start_date: str, stop_date: str) -> None:
    total_row_start = 1
    print(f"Appending all totals for {num_days} days")
    total_row_end = num_days + num_days * 97

    all_total_formula_row = []
    for col_index, user in enumerate(found_users.values(), start=1):
        column_letter = chr(ord('A') + col_index)
        all_total_minutes = f"SUM(ArrayFormula(VALUE(SPLIT(FILTER({column_letter}{total_row_start}:{column_letter}{total_row_end}, REGEXMATCH(A{total_row_start}:A{total_row_end}, \"TOTAL*\")), \":\")) * {{60, 1}}))"
        formatted_time_formula = f"=TEXT(INT({all_total_minutes} / 60), \"0\") & \":\" & TEXT(MOD({all_total_minutes}, 60), \"00\")"

        all_total_formula_row.append(formatted_time_formula)

    all_total_row = [f'ALL TOTAL [{start_date} / {stop_date}]'] + all_total_formula_row
    separator_row = ['-' * 20] * len(all_total_row)

    worksheet.append_rows([separator_row, all_total_row, separator_row], value_input_option='USER_ENTERED')


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