from datetime import datetime, timedelta
import requests
import json

from clockify_scraping.clockify_api import ClockifyAPI
from clockify_scraping.config.settings import Settings
import time
import gspread
from datetime import datetime, timedelta
from clockify_api import ClockifyAPI
from clockify_scraping.sheet_connect import GoogleSheetAPI

def get_data():
    clockify_api = ClockifyAPI(api_key=Settings.CLOCKIFY_API_KEY)

    all_projects = {}

    ws_projects_api = clockify_api.get_all_projects_in_workspace(Settings.CLOCKIFY_WORKSPACE_ID)

    now = datetime.now()
    first_day_current_month = now.replace(day=1).strftime('%Y-%m-%d')
    first_day_next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1).strftime('%Y-%m-%d')

    for project in ws_projects_api:
        all_projects[project['name']] = {
            'id': project['id'],
            'work_duration': f'[{first_day_current_month} / {first_day_next_month}]',
        }
    
    print("All projects:")
    print(json.dumps(all_projects, indent=4))
    
    all_users = []

    ws_users_api = clockify_api.get_workspace_users(Settings.CLOCKIFY_WORKSPACE_ID)
    for user in ws_users_api:
        all_users.append({user['name']: user['id']})
    
    print("All users:")
    print(json.dumps(all_users, indent=4))

    users_by_project = {}

    for project in all_projects:
        project_id = all_projects[project]['id']
        users = clockify_api.get_workspace_users(Settings.CLOCKIFY_WORKSPACE_ID, params={'projectId': project_id})
        users_by_project[project] = [user['name'] for user in users]
    print("Users by project:")
    print(json.dumps(users_by_project, indent=4))


def initialize_sheets(sheet_api: GoogleSheetAPI, projects):
    for project in projects:
        sheet_name = f"{project} {projects[project]['work_duration']}"
        try:
            sheet_api.open_sheet().worksheet(sheet_name)
            print(f"Sheet {sheet_name} already exists.")
        except gspread.exceptions.WorksheetNotFound:
            try:
                sheet_api.open_sheet().add_worksheet(title=sheet_name, rows="1000", cols="26")
            except gspread.exceptions.APIError as e:
                print(f"Error creating sheet {sheet_name}: {e}")

def update_sheet(sheet_api: GoogleSheetAPI, project, users, time_entries):
    now = datetime.now()
    sheet_name = f"{project} [{now.strftime('%Y-%m-01')} / {(now + timedelta(days=32)).replace(day=1).strftime('%Y-%m-01')}]"
    try:
        worksheet = sheet_api.open_sheet().worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet_api.open_sheet().add_worksheet(title=sheet_name, rows="1000", cols="26")
        worksheet = sheet_api.open_sheet().worksheet(sheet_name)

    headers = ["Time Slot"] + list(users.keys())
    worksheet.update(range_name='A1', values=[headers])

    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    time_slots = [(day_start + timedelta(minutes=15*i)).strftime('%H:%M') for i in range(96)]
    worksheet.update(range_name='A2:A97', values=[[slot] for slot in time_slots])

    for entry in time_entries:
        user_name = next(user for user, id in users.items() if id == entry['userId'])
        start_time = datetime.strptime(entry['timeInterval']['start'], '%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_time.strftime('%H:%M')
        
        if start_time_str in time_slots:
            time_slot_index = time_slots.index(start_time_str) + 2
            col_index = headers.index(user_name) + 1
            worksheet.update_cell(time_slot_index, col_index, entry['description'])
        else:
            print(f"Time slot {start_time_str} not found in time slots list")

def fetch_and_update_data(clockify_api: ClockifyAPI, sheet_api: GoogleSheetAPI, projects):
    for project_name, project_info in projects.items():
        users = clockify_api.get_workspace_users(Settings.CLOCKIFY_WORKSPACE_ID, params={'projectId': project_info['id']})
        users_dict = {user['name']: user['id'] for user in users}
        now = datetime.utcnow()
        fifteen_minutes_ago = now - timedelta(minutes=1)
        time_entries = []
        for user_id in users_dict.values():
            params = {
                'start': fifteen_minutes_ago.isoformat() + 'Z',
                'end': now.isoformat() + 'Z',
                'project': project_info['id']
            }
            entries = clockify_api.get_time_entries_for_user(user_id, params)
            time_entries.extend(entries)
        update_sheet(sheet_api, project_name, users_dict, time_entries)

if __name__ == '__main__':
    clockify_api = ClockifyAPI(api_key=Settings.CLOCKIFY_API_KEY)
    sheet_api = GoogleSheetAPI(spreadsheet_id=Settings.SPREADSHEET_ID, credentials_path=Settings.GOOGLE_SHEETS_CREDENTIALS_FILE, token_path=Settings.GOOGLE_OAUTH_TOKEN_FILE)
    
    ws_projects_api = clockify_api.get_all_projects_in_workspace(Settings.CLOCKIFY_WORKSPACE_ID)
    now = datetime.now()
    first_day_current_month = now.replace(day=1).strftime('%Y-%m-%d')
    first_day_next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1).strftime('%Y-%m-%d')

    all_projects = {
        project['name']: {
            'id': project['id'],
            'work_duration': f'[{first_day_current_month} / {first_day_next_month}]'
        } for project in ws_projects_api
    }
    
    initialize_sheets(sheet_api, all_projects)
    while True: 
        fetch_and_update_data(clockify_api, sheet_api, all_projects)
        time.sleep(60)