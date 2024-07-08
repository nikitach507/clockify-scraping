import json
import requests
from sheetify.config.settings import Settings


class ClockifyAPI:
    def __init__(self, api_key: str) -> None:
        self.headers = {
            'X-Api-Key': api_key,
            'Content-Type': 'application/json'
        }

    def get_workspace_users(self, workspace_id: str, params: dict=None) -> dict:
        """
        Get all users in a workspace

        Args:
            workspace_id (str): The workspace ID
            params (dict): Query parameters -> projectId, memberships
        
        Returns:
            dict: The response JSON

        """
        url = f"{Settings.CLOCKIFY_BASE_URL}/workspaces/{workspace_id}/users"
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def get_all_projects_in_workspace(self, workspace_id: str, params: dict=None) -> dict:
        """
        Get all projects in a workspace

        Args:
            workspace_id (str): The workspace ID
            params (dict): Query parameters -> name
        
        Returns:
            dict: The response JSON

        """
        url = f"{Settings.CLOCKIFY_BASE_URL}/workspaces/{workspace_id}/projects"
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def get_time_entries_for_user(self, user_id: str, params: dict=None) -> dict:
        """
        Get time entries for a user

        Args:
            user_id (str): The user ID
            params (dict): Query parameters -> start, end, description, project
        
        Returns:
            dict: The response JSON

        """
        url = f"{Settings.CLOCKIFY_BASE_URL}/workspaces/{Settings.CLOCKIFY_WORKSPACE_ID}/user/{user_id}/time-entries"
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    

if __name__ == '__main__':
    clockify_api = ClockifyAPI(api_key=Settings.CLOCKIFY_API_KEY)

    try:
        users = clockify_api.get_workspace_users(workspace_id=Settings.CLOCKIFY_WORKSPACE_ID, params={'projectId': '66852f018884d32751006bf5'})
        print("Users in workspace:")
        print(json.dumps(users, indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Error fetching users: {err}")
    
    try:
        projects = clockify_api.get_all_projects_in_workspace(workspace_id=Settings.CLOCKIFY_WORKSPACE_ID)
        print("Projects in workspace:")
        print(json.dumps(projects, indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Error fetching projects: {err}")

    if users:
        first_user_id = users[0]['id']
        try:
            time_entries = clockify_api.get_time_entries_for_user(user_id=first_user_id)
            print(f"Time entries for user")
            print(json.dumps(time_entries, indent=4))
        except requests.exceptions.HTTPError as err:
            print(f"Error fetching time entries: {err}")