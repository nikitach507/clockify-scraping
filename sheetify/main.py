from datetime import datetime, timedelta
import requests
import json
import argparse

from sheetify.clockify_api import ClockifyAPI
from sheetify.config.settings import Settings

def add_project(project_name, start_date, end_date):
    """
    Add a project with specified name and date range.

    Args:
        project_name (str): Name of the project.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    """
    print(f'Adding project "{project_name}" from {start_date} to {end_date}')

def delete_project(project_name, start_date, end_date):
    """
    Delete a project with specified name and date range.

    Args:
        project_name (str): Name of the project.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    """
    print(f'Deleting project "{project_name}" from {start_date} to {end_date}')

def validate_date_format(date_str):
    """
    Validate date format to ensure it matches YYYY-MM-DD.

    Args:
        date_str (str): Date string to validate.

    Raises:
        argparse.ArgumentTypeError: If date format is invalid.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f'Invalid date format: {date_str}. Use YYYY-MM-DD.')

def validate_date_order(start_date, end_date):
    """
    Validate date order to ensure start date is before end date.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Raises:
        argparse.ArgumentTypeError: If end date is not after start date.
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    if start > end:
        raise argparse.ArgumentTypeError('End date must be after start date.')
    
def main():
    parser = argparse.ArgumentParser(prog='sheetify', description='Clockify project management', usage='%(prog)s <command> [options]')

    # Subcommands: add and delete
    subparsers = parser.add_subparsers(title='Commands', description='Available commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a project')
    add_parser.add_argument('--project', '-p', required=True, help='Name of the project')
    add_parser.add_argument('--start', '-s', required=True, help='Start date (YYYY-MM-DD)')
    add_parser.add_argument('-e', '--end', required=True, help='End date (YYYY-MM-DD)')
    add_parser.set_defaults(func=add_project)

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a project')
    delete_parser.add_argument('--project', '-p', required=True, help='Name of the project')
    delete_parser.add_argument('--start', '-s', required=True, help='Start date (YYYY-MM-DD)')
    delete_parser.add_argument('--end', '-e', required=True, help='End date (YYYY-MM-DD)')
    delete_parser.set_defaults(func=delete_project)

    args = parser.parse_args()

    validate_date_format(args.start)
    validate_date_format(args.end)
    validate_date_order(args.start, args.end)

    args.func(args.project, args.start, args.end)

        
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
