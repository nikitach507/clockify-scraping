from datetime import datetime, timedelta, timezone
import os
import re
import json
import click
from tqdm import tqdm
from xlsxwriter import Workbook
from reportify.clockify_handler import ClockifyAPI
from reportify.config.settings import (
    SPREADSHEET_ID, CLOCKIFY_API_KEY, CLOCKIFY_WORKSPACE_ID,
    GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_OAUTH_TOKEN_FILE, EXCEL_DIRECTORY
)
from reportify.sheet_handler import GoogleSheetAPI
from reportify.excel_handler import append_data_to_sheet, append_all_totals, set_column_widths

def validate_dates(start_date: datetime, end_date: datetime) -> tuple[str, str]:
    if start_date > end_date:
        raise click.BadParameter('End date must be after start date.')
    if start_date > datetime.now():
        raise click.BadParameter('Start date cannot be in the future.')
    if end_date > datetime.now():
        raise click.BadParameter('End date cannot be in the future.')

def validate_auth_data(api_key: str, workspace_id: str, google_creds: str, google_sheet_id: str, dir_path: str) -> None:
    if api_key and not re.match(r'^[0-9a-zA-Z]{48}$', api_key):
        raise click.BadParameter('Invalid API key.')
    if workspace_id and not re.match(r'^[0-9a-z]{24}$', workspace_id):
        raise click.BadParameter('Invalid workspace ID.')
    if google_creds and (not os.path.exists(google_creds) or not json.load(open(google_creds))):
        raise click.BadParameter('Invalid Google credentials file.')
    if google_sheet_id and not re.match(r'^[a-zA-Z0-9-_]{44}$', google_sheet_id):
        raise click.BadParameter('Invalid Google Sheet ID.')
    if dir_path and not os.path.exists(dir_path):
        raise click.BadParameter('Invalid directory path.')

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-t', '--type', required=True, type=click.Choice(['excel', 'sheet'], case_sensitive=False), help='Report type')
@click.option('-p', '--project', required=True, help='Name of the project')
@click.option('-s', '--start', required=True, help='Start date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('-e', '--stop', required=True, help='End date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--api-key', prompt=False, help='Clockify API key')
@click.option('--workspace-id', prompt=False, help='Clockify workspace ID')
@click.option('--google-creds', prompt=False, help='Path to Google Sheets credentials JSON file')
@click.option('--google-sheet-id', prompt=False, help='Google Sheet ID to append data to')
@click.option('--dir-path', prompt=False, help='Path to directory where the Excel file will be saved')
def main(type: str, project: str, start: datetime, stop: datetime, api_key: str | None, workspace_id: str | None, google_creds: str | None, google_sheet_id: str | None, dir_path: str | None):
    print("")
    validate_auth_data(api_key, workspace_id, google_creds, google_sheet_id, dir_path)
    validate_dates(start, stop)

    clockify_api = ClockifyAPI(api_key=CLOCKIFY_API_KEY if not api_key else api_key,workspace_id=CLOCKIFY_WORKSPACE_ID if not workspace_id else workspace_id)
    
    total_days = (stop - start).days + 1
    project_data = clockify_api.initialize_project_data(project)
    file_name = f"{project_data['name']} [{start.date()} | {stop.date()}]"

    all_users = clockify_api.get_workspace_users()
    first_day = start.replace(hour=0, minute=15, tzinfo=timezone.utc)
    last_day = (stop + timedelta(days=1)).replace(hour=0, tzinfo=timezone.utc)
    users_in_work = clockify_api.get_users_in_work(all_users, project_data['id'], first_day, last_day)
    if not users_in_work:
        print("No users found in the project for the given period. Exiting without creating a new file.")
        exit(0)

    active_users_name, active_users_id = list(users_in_work.keys()), list(users_in_work.values())

    if type == 'sheet':
        google_sheet_id = google_sheet_id if google_sheet_id else SPREADSHEET_ID
        sheet_api = GoogleSheetAPI(spreadsheet_id=google_sheet_id, credentials_path=GOOGLE_SHEETS_CREDENTIALS_FILE if not google_creds else google_creds, token_path=GOOGLE_OAUTH_TOKEN_FILE)
        sheet_api.prepare_worksheet(file_name)
        sheet_url = f"https://docs.google.com/spreadsheets/d/{google_sheet_id}/edit#gid={sheet_api.sheet_id}"

        sheet_api._safety_append_rows([f"HARDWARIO Report for Period from {start.date()} to {stop.date()}"] + [""], row=True)
        header_len = max(len(active_users_id) + 1, 5)
        sheet_api.header_formating(0, 0, header_len)
        sheet_api._safety_append_rows(["·"], row=True)
    else:
        dir_path = dir_path if dir_path else EXCEL_DIRECTORY
        excel_path = os.path.join(dir_path, f"{file_name}.xlsx")
        excel_url = f'file://{os.path.abspath(excel_path)}'
        if os.path.exists(excel_path):
            print(f"File '{excel_path}' already exists. Exiting without creating a new file.")
            exit(0)

        workbook = Workbook(excel_path)
        worksheet = workbook.add_worksheet()
        header_len = max(len(active_users_id), 5)
        worksheet.write_row(0, 0, [f"HARDWARIO Report for Period from {start.date()} to {stop.date()}"] + [""] * header_len, workbook.add_format({'bold': True, 'font_size': 20, 'bg_color': 'FFE3E6', 'color': 'AC3A4D'}))
        worksheet.write_row(1, 0, [""])
    
    current_date = start
    row_index = 4 if type == 'sheet' else 2
    time_slots = [(first_day + timedelta(minutes=15 * slot)).strftime('%H:%M') for slot in range(96)]
    progress_bar = tqdm(total=int(total_days), desc='Processing', unit='day', leave=True, colour='#3FDCEE', ascii=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}{postfix}]')
    
    while current_date <= stop:
        day_begin = current_date.replace(hour=0, minute=15, tzinfo=timezone.utc)
        day_finish = day_begin + timedelta(days=1)
        time_entries = clockify_api.fetch_time_entries(active_users_id, project_data['id'], day_begin, day_finish)

        sheet_data_to_send = [[str(current_date.date())] + active_users_name] + \
                             [[slot] + [time_entries[user].get(slot, '') for user in active_users_id] for slot in time_slots]

        if type == 'sheet':
            sheet_api.append_table_to_sheet(sheet_data_to_send, current_date, len(users_in_work), row_index)
            sheet_api._safety_append_rows(["·"], row=True)
        elif type == 'excel':
            append_data_to_sheet(workbook, worksheet, sheet_data_to_send, current_date, len(users_in_work), row_index)
            worksheet.write_row(row_index + 97, 0, [""])

        row_index += 99
        current_date += timedelta(days=1)
        progress_bar.update(1)

    if type == 'sheet':
        sheet_api.append_all_totals(int(total_days), users_in_work, start, stop)
    elif type == 'excel':
        append_all_totals(workbook, worksheet, int(total_days), active_users_name, row_index, start, stop)
        set_column_widths(worksheet, len(active_users_name) + 1, {1: 20.0, 2: 20.0})
        workbook.close()

    progress_bar.close()
    print(f"\nData successfully written from Clockify. \nOpen the file here: {excel_url if type == 'excel' else sheet_url}")


if __name__ == '__main__':
    main()
