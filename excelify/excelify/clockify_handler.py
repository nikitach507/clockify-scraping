import click
import pytz
import requests
from excelify.config.pavel_settings import Settings
from datetime import datetime, timedelta, timezone
from collections import defaultdict


class ClockifyAPI:
    def __init__(self, api_key: str, workspace_id: str) -> None:
        self.headers = {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        self.workspace_id = workspace_id
        self._validate_clockify_data()

    def _validate_clockify_data(self) -> None:
        api_url = 'https://api.clockify.me/api/v1/user'
        response = requests.get(api_url, headers=self.headers)
        if response.status_code != 200:
            raise click.BadParameter('Invalid API key: User does not exist.')
        
        id_url = 'https://api.clockify.me/api/v1/workspaces'
        response = requests.get(id_url, headers=self.headers)
        if response.status_code != 200:
            raise click.BadParameter('Invalid workspace ID: Workspace does not exist.')
        
    @classmethod
    def round_time_to_nearest_quarter(cls, dt: datetime, round_up: bool = False) -> datetime:
        if round_up:
            dt += timedelta(minutes=15 - dt.minute % 15, seconds=-dt.second, microseconds=-dt.microsecond) # datetime: 1900-01-01 04:45:00+02:00
        else:
            dt -= timedelta(minutes=dt.minute % 15, seconds=dt.second, microseconds=dt.microsecond) # datetime: 1900-01-01 04:30:00+02:00
        return dt

    @classmethod
    def convert_to_local_time(cls, dt: datetime) -> datetime:
        return dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Prague')) # datetime: 1900-01-01 04:31:00+02:00

    def get_workspace_users(self, params: dict=None) -> dict:
        """
        Get all users in a workspace

        Args:
            workspace_id (str): The workspace ID
            params (dict): Query parameters -> projectId, memberships
        
        Returns:
            dict: The response JSON

        """
        url = f"{Settings.CLOCKIFY_BASE_URL}/workspaces/{self.workspace_id}/users"
        try:
            response = requests.get(url, headers=self.headers, params=params)

            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Error fetching users: {err}")
            raise
    
    def get_all_projects_in_workspace(self, params: dict=None) -> dict:
        """
        Get all projects in a workspace

        Args:
            workspace_id (str): The workspace ID
            params (dict): Query parameters -> name
        
        Returns:
            dict: The response JSON

        """
        url = f"{Settings.CLOCKIFY_BASE_URL}/workspaces/{self.workspace_id}/projects"
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def initialize_project_data(self, project_name: str) -> dict:
        projects = self.get_all_projects_in_workspace()
        project = next((p for p in projects if p['name'] == project_name), None)
        if project:
            return {'id': project['id'], 'name': project['name']}
        
        raise click.BadParameter(f'Project "{project_name}" does not exist in the workspace.')
    
    def get_time_entries_for_user(self, user_id: str, params: dict=None) -> dict:
        """
        Get time entries for a user

        Args:
            user_id (str): The user ID
            params (dict): Query parameters -> start, end, description, project
        
        Returns:
            dict: The response JSON

        """
        url = f"{Settings.CLOCKIFY_BASE_URL}/workspaces/{self.workspace_id}/user/{user_id}/time-entries"
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def fetch_time_entries(self, users_id, project_id: str, start_of_day: datetime, end_of_day: datetime) -> dict:
        time_entries = defaultdict(lambda: defaultdict(str))

        for user_id in users_id:
            time_entries_by_user = self.get_time_entries_for_user(user_id, params={'project': project_id, 'start': start_of_day.isoformat(), 'end': end_of_day.isoformat()})

            for time_entry in time_entries_by_user:
                start_of_work = self.convert_to_local_time(datetime.fromisoformat(time_entry['timeInterval']['start']).replace(tzinfo=timezone.utc)) # datetime: 1900-01-01 04:31:00+02:00
                end_of_work = self.convert_to_local_time(datetime.now(timezone.utc).replace(tzinfo=timezone.utc) 
                                                    if time_entry['timeInterval']['end'] is None 
                                                    else datetime.fromisoformat(time_entry['timeInterval']['end']).replace(tzinfo=timezone.utc)) # datetime: 1900-01-01 04:41:00+02:00

                
                start_of_work = self.round_time_to_nearest_quarter(start_of_work, round_up=True) # datetime: 1900-01-01 04:30:00+02:00
                if end_of_work.minute % 15 != 0:
                    end_of_work = self.round_time_to_nearest_quarter(end_of_work, round_up=True) # datetime: 1900-01-01 04:45:00+02:00
                
                while start_of_work <= end_of_work:
                    time_slot = start_of_work.strftime('%H:%M') # str: 04:30
                    time_entries[user_id][time_slot] = time_entry['description']
                    start_of_work += timedelta(minutes=15) # datetime: 1900-01-01 04:45:00+02:00
        
        return time_entries

    def get_users_in_work(self, all_users: dict, project_id: str, first_day: datetime, last_day: datetime) -> dict:
        users_in_work = {}

        for user in all_users:
            time_entries = self.get_time_entries_for_user(user['id'], params={
                'project': project_id,
                'start': first_day.isoformat(),
                'end': last_day.isoformat()
            })

            if time_entries:
                users_in_work[user['name']] = user['id']
        
        return users_in_work