from datetime import datetime, timedelta, timezone
from tqdm import tqdm
import json
import os
import click
import re
from sheetify.clockify_handler import ClockifyAPI
from sheetify.config.settings import SPREADSHEET_ID, CLOCKIFY_API_KEY, CLOCKIFY_WORKSPACE_ID, GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_OAUTH_TOKEN_FILE, WORKSPACE_NAME
from sheetify.sheet_handler import GoogleSheetAPI


def click_validate_dates(start_date: datetime, end_date: datetime) -> None:
    if start_date > end_date:
        raise click.BadParameter('End date must be after start date.')
    if start_date > datetime.now():
        raise click.BadParameter('Start date cannot be in the future.')
    if end_date > datetime.now():
        raise click.BadParameter('End date cannot be in the future.')


def click_validate_auth_data(api_key: str, workspace_id: str, google_creds: str, google_sheet_id: str) -> None:
    if api_key and not re.match(r'^[0-9a-zA-Z]{48}$', api_key):
        raise click.BadParameter('Invalid API key.')
    if workspace_id and not re.match(r'^[0-9a-z]{24}$', workspace_id):
        raise click.BadParameter('Invalid workspace ID.')
    if google_creds:
        if not os.path.exists(google_creds):
            raise click.BadParameter('Google credentials file does not exist.')
        try:
            with open(google_creds, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            raise click.BadParameter('Google credentials file is not a valid JSON.')
    if google_sheet_id and not re.match(r'^[a-zA-Z0-9-_]{44}$', google_sheet_id):
        raise click.BadParameter('Invalid Google Sheet ID format.')


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-p', '--project', required=True, help='Name of the project')
@click.option('-s', '--start', required=True, help='Start date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('-e', '--stop', required=True, help='End date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--api-key', prompt=False, help='Clockify API key')
@click.option('--workspace-id', prompt=False, help='Clockify workspace ID')
@click.option('--google-creds', prompt=False, help='Path to Google Sheets credentials JSON file')
@click.option('--google-sheet-id', prompt=False, help='Google Sheet ID to append data to')
def main(project: str, start: datetime, stop: datetime, api_key: str | None, workspace_id: str | None, google_creds: str | None, google_sheet_id: str | None):
    click_validate_dates(start, stop)
    click_validate_auth_data(api_key, workspace_id, google_creds, google_sheet_id)
    total_days = float((stop - start).days) + 1
    start, stop = str(start.date()), str(stop.date())  # str: 1900-01-01
    google_sheet_id = google_sheet_id if google_sheet_id else SPREADSHEET_ID
    print("")

    clockify_api = ClockifyAPI(api_key=CLOCKIFY_API_KEY if not api_key else api_key,
                               workspace_id=CLOCKIFY_WORKSPACE_ID if not workspace_id else workspace_id)
    sheet_api = GoogleSheetAPI(spreadsheet_id=google_sheet_id,
                               credentials_path=GOOGLE_SHEETS_CREDENTIALS_FILE if not google_creds else google_creds,
                               token_path=GOOGLE_OAUTH_TOKEN_FILE)

    try:
        project_data = clockify_api.initialize_project_data(project)
    except click.BadParameter as e:
        print(e)
        exit(0)

    sheet_name = f"{project_data['name']} [{start} / {stop}]"
    sheet_id = sheet_api.prepare_worksheet(sheet_name)

    all_users = clockify_api.get_workspace_users()

    first_day = datetime.strptime(start, '%Y-%m-%d').replace(hour=0, minute=15, second=0, microsecond=0, tzinfo=timezone.utc)
    last_day = (datetime.strptime(stop, '%Y-%m-%d') + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    users_in_work = clockify_api.get_users_in_work(all_users, project_data['id'], first_day, last_day)
    if not users_in_work:
        print("No users found in the project for the given period. Exiting without creating a new file.")
        print("")
        exit(0)

    active_users_name = list(users_in_work.keys())
    active_users_id = list(users_in_work.values())

    progress_bar = tqdm(total=int(total_days), desc='Processing', unit='day', leave=True, colour='#3FDCEE',
                        ascii=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}{postfix}]')

    if WORKSPACE_NAME is None:
        sheet_api._safety_append_rows([f"Report for Period from {start} to {stop}"] + [""], row=True)
    else:
        sheet_api._safety_append_rows([f"{WORKSPACE_NAME} Report for Period from {start} to {stop}"] + [""], row=True)
    
    header_len = len(active_users_id) + 1 if len(active_users_id) > 4 else 5
    sheet_api.header_formating(0, 0, header_len)

    sheet_api._safety_append_rows(["·"], row=True)
    current_date = start
    row_index = 4

    while current_date <= stop:
        day_begin = datetime.strptime(current_date, '%Y-%m-%d').replace(hour=0, minute=15, second=0, microsecond=0, tzinfo=timezone.utc)  # datetime: 1900-01-01 00:15:00+02:00
        day_finish = (day_begin + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)  # datetime: 1900-01-02 00:00:00+02:00
        time_entries = clockify_api.fetch_time_entries(active_users_id, project_data['id'], day_begin, day_finish)

        header_row = [current_date] + active_users_name
        sheet_data_to_send = [header_row]

        for time_slot in range(0, 96):
            time_period = (day_begin + timedelta(minutes=15 * time_slot)).strftime('%H:%M')  # str: 04:30
            row = [time_period] + [time_entries[user_id].get(time_period, '') for user_id in active_users_id]
            sheet_data_to_send.append(row)

        sheet_api.append_table_to_sheet(sheet_data_to_send, current_date, len(users_in_work), row_index)

        sheet_api._safety_append_rows(["·"], row=True)
        row_index += 99
        current_date = (day_begin + timedelta(days=1)).strftime('%Y-%m-%d')  # str: 1900-01-02
        progress_bar.update(1)

    sheet_api.append_all_totals(int(total_days), users_in_work, start, stop)
    progress_bar.close()

    print("")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{google_sheet_id}/edit#gid={sheet_id}"
    print(f"Data successfully updated in Google Sheets. \nOpen the file here: {sheet_url}")


if __name__ == '__main__':
    main()
