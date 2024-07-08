from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    CLOCKIFY_API_KEY = os.getenv('CLOCKIFY_API_KEY')
    CLOCKIFY_BASE_URL = os.getenv('CLOCKIFY_BASE_URL')
    CLOCKIFY_WORKSPACE_ID = os.getenv('CLOCKIFY_WORKSPACE_ID')
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    GOOGLE_OAUTH_TOKEN_FILE = os.getenv('GOOGLE_OAUTH_TOKEN_FILE')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
