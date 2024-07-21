from datetime import datetime, timedelta, timezone
import os
import click
import re
from tqdm import tqdm
from openpyxl import Workbook
from excelify.clockify_handler import ClockifyAPI
from excelify.config.pavel_settings import Settings
from excelify.sheet_handler import append_data_to_sheet, append_all_totals


def click_validate_dates(start_date: datetime, end_date: datetime) -> tuple[str, str]:
    if start_date > end_date:
        raise click.BadParameter('End date must be after start date.')
    if start_date > datetime.now():
        raise click.BadParameter('Start date cannot be in the future.')
    if end_date > datetime.now():
        raise click.BadParameter('End date cannot be in the future.')

    return str(start_date.date()), str(end_date.date())
    

def click_validate_auth_data(api_key: str, workspace_id: str, dir_path: str) -> None:
    if api_key and not re.match(r'^[0-9a-zA-Z]{48}$', api_key):
        raise click.BadParameter('Invalid API key.')
    if workspace_id and not re.match(r'^[0-9a-z]{24}$', workspace_id):
        raise click.BadParameter('Invalid workspace ID.')
    if dir_path and not os.path.exists(dir_path):
        raise click.BadParameter('Invalid directory path.')
        

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-p', '--project', required=True, help='Name of the project')
@click.option('-s', '--start', required=True, help='Start date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('-e', '--stop', required=True, help='End date (YYYY-MM-DD)', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--api-key', prompt=False, help='Clockify API key')
@click.option('--workspace-id', prompt=False, help='Clockify workspace ID')
@click.option('--dir_path', prompt=False, help='Path to directory where the Excel file will be saved')
def main(project: str, start: datetime, stop: datetime, api_key: str | None, workspace_id: str| None, dir_path: str| None):
    print("")
    dir_path = dir_path if dir_path else Settings.EXCEL_DIRECTORY

    try:
        total_days = float((stop - start).days) + 1
        start, stop = click_validate_dates(start, stop) # str: 1900-01-01
        click_validate_auth_data(api_key, workspace_id, dir_path)

        clockify_api = ClockifyAPI(api_key=Settings.CLOCKIFY_API_KEY if not api_key else api_key,
                                   workspace_id=Settings.CLOCKIFY_WORKSPACE_ID if not workspace_id else workspace_id)
        project_data = clockify_api.initialize_project_data(project)
    except click.BadParameter as e:
        print(e)
        exit(0)

    file_name = f"{project_data['name']} [{start} | {stop}]"
    file_path = os.path.join(dir_path, f"{file_name}.xlsx")
    if os.path.exists(file_path):
        print(f"File '{file_path}' already exists. Exiting without creating a new file.")
        exit(0)

    workbook = Workbook()
    worksheet = workbook.active

    all_users = clockify_api.get_workspace_users()

    first_day = datetime.strptime(start, '%Y-%m-%d').replace(hour=0, minute=15, second=0, microsecond=0, tzinfo=timezone.utc)
    last_day = (datetime.strptime(stop, '%Y-%m-%d') + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    users_exclusion = clockify_api.get_users_exclusion(all_users, project_data['id'], first_day, last_day)

    users_in_work = {user['name']: user['id'] for user in all_users if user['id'] not in users_exclusion}

    progress_bar = tqdm(total=int(total_days), desc='Processing', unit='day', leave=True, colour='#3FDCEE', 
                        ascii=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}{postfix}]')
    
    current_date = start
    row_index = 2

    while current_date <= stop:
        day_begin = datetime.strptime(current_date, '%Y-%m-%d').replace(hour=0, minute=15, second=0, microsecond=0, tzinfo=timezone.utc) # datetime: 1900-01-01 00:15:00+02:00
        day_finish = (day_begin + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc) # datetime: 1900-01-02 00:00:00+02:00
        time_entries = clockify_api.fetch_time_entries(list(users_in_work.values()), project_data['id'], day_begin, day_finish)

        header_row = [current_date] + list(users_in_work.keys())
        sheet_data_to_send = [header_row]
        
        for time_slot in range(0, 96):
            time_period = (day_begin + timedelta(minutes=15 * time_slot)).strftime('%H:%M') # str: 04:30
            row = [time_period] + [time_entries[user_id].get(time_period, '') for user_id in list(users_in_work.values())]
            sheet_data_to_send.append(row)
            
        append_data_to_sheet(worksheet, sheet_data_to_send, current_date, len(users_in_work), row_index)
        
        row_index += 99
        current_date = (day_begin + timedelta(days=1)).strftime('%Y-%m-%d') # str: 1900-01-02
        progress_bar.update(1)

        worksheet.append(["·"])

    append_all_totals(worksheet, int(total_days), len(users_in_work), start, stop)
    workbook.save(file_path)
    progress_bar.close()
    print("")

    file_url = f'file://{os.path.abspath(file_path)}'
    print(f"Data successfully updated in the Excel file. \nOpen the file here: {file_url}")
    

if __name__ == '__main__':
    main()
