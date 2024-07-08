from datetime import datetime, timedelta
import requests
import json

from clockify_scraping.clockify_api import ClockifyAPI
from clockify_scraping.config.settings import Settings


def main():
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


if __name__ == '__main__':
    main()
