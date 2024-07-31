import os
import sys

def check_required_env_vars():
    required_vars = [
        'WORKSPACE_NAME',
        'CLOCKIFY_API_KEY',
        'CLOCKIFY_BASE_URL',
        'CLOCKIFY_WORKSPACE_ID',
        'GOOGLE_SHEETS_CREDENTIALS_FILE',
        'GOOGLE_OAUTH_TOKEN_FILE',
        'SPREADSHEET_ID'
    ]
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

try:
    check_required_env_vars()
except EnvironmentError as e:
    print("Error: One or more required environment variables are missing.")
    print(e)
    print("\nPlease follow these steps to set the required environment variables:")
    print("1. Identify the missing environment variables from the list above.")
    print("2. Set these variables in your system's environment settings.")
    print("   - On Unix-based systems (e.g., macOS, Linux), you can set them in your shell configuration file (e.g., .bashrc, .zshrc).")
    print("   - On Windows, you can set them via System Properties -> Environment Variables.")
    print("3. Restart your terminal or IDE to ensure the variables are loaded.")
    print("\nFor more details on setting environment variables, refer to the documentation for your operating system.")
    sys.exit(1)

WORKSPACE_NAME = os.getenv('WORKSPACE_NAME', None)
CLOCKIFY_API_KEY = os.getenv('CLOCKIFY_API_KEY')
CLOCKIFY_BASE_URL = os.getenv('CLOCKIFY_BASE_URL', 'https://api.clockify.me/api/v1')
CLOCKIFY_WORKSPACE_ID = os.getenv('CLOCKIFY_WORKSPACE_ID')
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
GOOGLE_OAUTH_TOKEN_FILE = os.getenv('GOOGLE_OAUTH_TOKEN_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')