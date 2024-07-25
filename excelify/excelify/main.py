from datetime import datetime, timedelta, timezone
import os
import click
import re
from tqdm import tqdm
from xlsxwriter import Workbook
from excelify.clockify_handler import ClockifyAPI
from excelify.config.settings import CLOCKIFY_API_KEY, CLOCKIFY_WORKSPACE_ID, EXCEL_DIRECTORY
from excelify.sheet_handler import append_data_to_sheet, append_all_totals
from excelify.sheet_handler import set_column_widths


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
    dir_path = dir_path if dir_path else EXCEL_DIRECTORY

    try:
        total_days = float((stop - start).days) + 1
        start, stop = click_validate_dates(start, stop) # str: 1900-01-01
        click_validate_auth_data(api_key, workspace_id, dir_path)

        clockify_api = ClockifyAPI(api_key=CLOCKIFY_API_KEY if not api_key else api_key,
                                   workspace_id=CLOCKIFY_WORKSPACE_ID if not workspace_id else workspace_id)
        project_data = clockify_api.initialize_project_data(project)
    except click.BadParameter as e:
        print(e)
        exit(0)

    file_name = f"{project_data['name']} [{start} | {stop}].xlsx"
    file_path = os.path.join(dir_path, file_name)
    if os.path.exists(file_path):
        print(f"File '{file_path}' already exists. Exiting without creating a new file.")
        exit(0)

    workbook = Workbook(file_path)
    worksheet = workbook.add_worksheet()

    all_users = clockify_api.get_workspace_users()

    first_day = datetime.strptime(start, '%Y-%m-%d').replace(hour=0, minute=15, second=0, microsecond=0, tzinfo=timezone.utc)
    last_day = (datetime.strptime(stop, '%Y-%m-%d') + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    users_in_work = clockify_api.get_users_in_work(all_users, project_data['id'], first_day, last_day)
    if not users_in_work:
        print("No users found in the project for the given period. The table will be created on the basis of an empty user.")
        users_in_work["User"] = 0
        
    active_users_name = list(users_in_work.keys())
    active_users_id = list(users_in_work.values())

    progress_bar = tqdm(total=int(total_days), desc='Processing', unit='day', leave=True, colour='#3FDCEE', 
                        ascii=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}{postfix}]')
    
    worksheet.write_row(0, 0, [f"HARDWARIO Report for Period from {start} to {stop}"] + [""] * len(active_users_name), 
                        workbook.add_format({'bold': True, 'font_size': 20, 'bg_color': 'FFC7CE', 'color': '9C0006'}))
    worksheet.write_row(1, 0, [""])
    
    current_date = start
    row_index = 2

    while current_date <= stop:
        day_begin = datetime.strptime(current_date, '%Y-%m-%d').replace(hour=0, minute=15, second=0, microsecond=0, tzinfo=timezone.utc) # datetime: 1900-01-01 00:15:00+02:00
        day_finish = (day_begin + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc) # datetime: 1900-01-02 00:00:00+02:00
        time_entries = clockify_api.fetch_time_entries(active_users_id, project_data['id'], day_begin, day_finish)

        header_row = [current_date] + active_users_name
        sheet_data_to_send = [header_row]
        
        for time_slot in range(0, 96):
            time_period = (day_begin + timedelta(minutes=15 * time_slot)).strftime('%H:%M') # str: 04:30
            row = [time_period] + [time_entries[user_id].get(time_period, '') for user_id in active_users_id]
            sheet_data_to_send.append(row)
        
        append_data_to_sheet(worksheet, workbook, sheet_data_to_send, current_date, len(users_in_work), row_index)

        current_date = (day_begin + timedelta(days=1)).strftime('%Y-%m-%d') # str: 1900-01-02
        progress_bar.update(1)
        row_index += 99

    append_all_totals(worksheet, workbook, int(total_days), active_users_name, row_index, start, stop)
    progress_bar.close()
    print("")

    file_url = f'file://{os.path.abspath(file_path)}'
    print(f"Data successfully updated in the Excel file. \nOpen the file here: {file_url}")
    set_column_widths(worksheet, len(active_users_name) + 1, {1: 20.0, 2: 20.0})
    workbook.close()

if __name__ == '__main__':
    main()
