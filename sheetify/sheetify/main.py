from collections import defaultdict
from datetime import datetime, timedelta, timezone
from tqdm import tqdm
import json
import os
import click
import re

from sheetify.clockify_handler import ClockifyAPI
from sheetify.config.nikita_settings import Settings
from sheetify.sheet_handler import GoogleSheetAPI, append_data_to_sheet, append_all_totals


def click_validate_dates(start_date: datetime, end_date: datetime) -> None:
    if start_date > end_date:
        raise click.BadParameter('End date must be after start date.')
    if start_date > datetime.now():
        raise click.BadParameter('Start date cannot be in the future.')
    if end_date > datetime.now():
        raise click.BadParameter('End date cannot be in the future.')
    
def click_validate_auth_data(start_date: datetime, end_date: datetime, api_key: str, workspace_id: str, google_creds: str, sheet_id: str) -> None:
    if api_key and not re.match(r'^[0-9a-zA-Z]{48}$', api_key):
        raise click.BadParameter('Invalid API key.')
    if workspace_id and not re.match(r'^[0-9a-z]{24}$', workspace_id):
        raise click.BadParameter('Invalid workspace ID.')
    if google_creds:
        if not os.path.isfile(google_creds):
            raise click.BadParameter('Google credentials file does not exist.')
        try:
            with open(google_creds, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            raise click.BadParameter('Google credentials file is not a valid JSON.')
    if sheet_id and not re.match(r'^[a-zA-Z0-9-_]{44}$', sheet_id):
        raise click.BadParameter('Invalid Google Sheet ID format.')
    

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-p', '--project', required=True, help='Name of the project')
@click.option('-s', '--start', required=True, help='Start date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('-e', '--stop', required=True, help='End date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--api-key', prompt=False, help='Clockify API key')
@click.option('--workspace-id', prompt=False, help='Clockify workspace ID')
@click.option('--google-creds', prompt=False, help='Path to Google Sheets credentials JSON file')
@click.option('--sheet-id', prompt=False, help='Google Sheet ID to append data to')
def main(project: str, start: datetime, stop: datetime, api_key: str | None, workspace_id: str| None, google_creds: str| None, sheet_id: str| None):
    click_validate_dates(start, stop)
    click_validate_auth_data(start, stop, api_key, workspace_id, google_creds, sheet_id)
    total_days = float((stop - start).days)
    start, stop = str(start.date()), str(stop.date()) # str: 1900-01-01
    sheet_id = sheet_id if sheet_id else Settings.SPREADSHEET_ID

    clockify_api = ClockifyAPI(api_key=Settings.CLOCKIFY_API_KEY if not api_key else api_key,
                               workspace_id=Settings.CLOCKIFY_WORKSPACE_ID if not workspace_id else workspace_id)
    sheet_api = GoogleSheetAPI(spreadsheet_id=sheet_id,
                               credentials_path=Settings.GOOGLE_SHEETS_CREDENTIALS_FILE if not google_creds else google_creds, 
                               token_path=Settings.GOOGLE_OAUTH_TOKEN_FILE)
    
    try:
        project_data = clockify_api.initialize_project_data(project)
    except click.BadParameter as e:
        print(e)
        exit(0) 
        
    sheet_name = f"{project_data['name']} [{start} / {stop}]"
    worksheet = sheet_api.prepare_worksheet(sheet_name)

    users_by_project = clockify_api.get_workspace_users(params={'projectId': project_data['id']})
    found_users = {user['name']: user['id'] for user in users_by_project}

    current_date = start
    row_index = 2

    progress_bar = tqdm(total=int(total_days), desc='Processing', unit='day')

    while current_date <= stop:
        day_begin = datetime.strptime(current_date, '%Y-%m-%d').replace(hour=0, minute=15, second=0, microsecond=0, tzinfo=timezone.utc) # datetime: 1900-01-01 00:15:00+02:00
        day_finish = (day_begin + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc) # datetime: 1900-01-02 00:00:00+02:00
        time_entries = clockify_api.fetch_time_entries(found_users.values(), project_data['id'], day_begin, day_finish)

        header_row = [current_date] + list(found_users.keys())
        sheet_data_to_send = [header_row]
        
        for time_slot in range(0, 96):
            time_period = (day_begin + timedelta(minutes=15 * time_slot)).strftime('%H:%M') # str: 04:30
            row = [time_period] + [time_entries[user_id].get(time_period, '-') for user_id in found_users.values()]
            sheet_data_to_send.append(row)
            
        append_data_to_sheet(worksheet, sheet_data_to_send, current_date, found_users, row_index)
        
        row_index += 98
        current_date = (day_begin + timedelta(days=1)).strftime('%Y-%m-%d') # str: 1900-01-02
        progress_bar.update(1)

    progress_bar.close()
    append_all_totals(worksheet, int(total_days), found_users, start, stop)
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    print(f"Data successfully updated in Google Sheets. Open the file here: {sheet_url}")

if __name__ == '__main__':
    main()
