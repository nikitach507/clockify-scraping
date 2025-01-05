# Sheetify

Sheetify is a command-line tool designed for extracting and processing time tracking data from Clockify and generating detailed Google Sheet reports. It helps users to easily compile and analyze their project-related time entries over specified periods.

With Sheetify, you can automate the process of retrieving time logs, formatting them into structured Google Sheet sheets, and generating comprehensive reports for effective time management and project analysis.

## Table of Contents

-  [Project Features](#project-features)
-  [Installation and Setup](#installation-and-setup)
-  [Configuration](#configuration)
-  [Package Features](#package-features)
    - [Command-Line Options](#command-line-options)
    - [Configuration Fallback](#configuration-fallback)
-  [License](#license)

## Project Features

- **Clockify API Integration**: 

    Seamlessly connects to the Clockify API to retrieve time tracking data for specified projects and dates.

- **Customizable Date Ranges**: 

    Allows users to specify the start and end dates for the report, ensuring flexibility in data extraction.

- **Project-Based Reporting**: 

    Generates reports based on specific projects, providing insights into time spent by users on project tasks.

- **Detailed Time Entries**: 

    Formats time tracking data into 15-minute intervals, offering granular insights into user activities.

- **Google Sheet Report Generation**: 

    Creates well-structured Google Sheet files with detailed tables, including headers, time slots, and user-specific data.

- **Summary and Totals**: 

    Computes and includes summary totals and overall time spent, both daily and for the entire report period.

## Installation and Setup

To set up and start using Sheetify, follow these steps:

1. Clone the Repository:

    ```sh
    git clone https://github.com/nikitach507/clockify-scraping.git
    ```

2. Navigate into the project directory:

    ```sh
    cd clockify-scraping/sheetify
    ```

3. Configure the Project:
Update the configuration settings to match your environment and requirements.

    ```sh
    nano sheetify/config/settings.py
    ```

4. Install the Required Package:

    ```sh
    poetry build
    ```

5. Install the package using pip:

    ```sh
    pip install --force-reinstall dist/sheetify-0.1.0.tar.gz
    ```

## Configuration

To configure Sheetify, you need to update the settings in the `settings.py` file located in the `config` directory. The following parameters must be set:

1. **Workspace Name**

    This optional parameter allows you to include a specific name for the workspace in the generated Google Sheet reports. If not set, a default label will be used.

    ```python
    WORKSPACE_NAME = 'your_workspace_name'
    ```
    > Set to None if you don't want to include a workspace name.

2. **Clockify API Key**:

    This is your personal API key for accessing the Clockify API.

    ```python
    CLOCKIFY_API_KEY = 'your_clockify_api_key'
    ```

    > You can obtain your Clockify API key from: Clockify account -> Preferences -> Advanced -> API.

3. **Clockify Base URL**:

    This is the base URL for the Clockify API. Typically, this should not need to be changed.

    ```python
    CLOCKIFY_BASE_URL = 'https://api.clockify.me/api/v1'
    ```

4. **Clockify Workspace ID**:

    This is the ID of the workspace you want to work with in Clockify. Replace the placeholder with your actual workspace ID.

    ```python
    CLOCKIFY_WORKSPACE_ID = 'your_clockify_workspace_id'
    ```

    > You can obtain your Clockify Workspace ID from: Workspaces -> Settings -> Get ID from URL.

5. **Google Sheets Credentials File**:

    This is the path to your Google Sheets credentials JSON file.

    ```bash
    export GOOGLE_SHEETS_CREDENTIALS_FILE='path/to/credentials.json'
    ```

    > You can obtain this file by creating a project in the Google Cloud Console, enabling the Google Sheets API, and generating OAuth 2.0 credentials. Download the JSON file and save it to your preferred directory.

6. **Google OAuth Token File**:

    This is the path to your Google OAuth token JSON file.

    ```bash
    export GOOGLE_OAUTH_TOKEN_FILE='path/to/token.json'
    ```

    > This file is generated the first time you run your application and go through the OAuth flow. The file will be saved automatically in the specified directory.

7. **Google Spreadsheet ID**:

    This is the ID of the Google Spreadsheet you want to append data to.

    ```bash
    export SPREADSHEET_ID='your_google_spreadsheet_id'
    ```

    > You can find the spreadsheet ID in the URL of your Google Sheet. It is the long string between /d/ and /edit.

## Package Features

The Sheetify package offers the following features and options for generating Google Sheet reports from Clockify data:

### Command-Line Options

- ```-p, --project (required)```:

    **Description**: Name of the project to generate the report for. \
    **Example**: -p "ProjectName"

- ```-s, --start (required)```:

    **Description**: Start date for the report in YYYY-MM-DD format. \
    **Example**: -s 2023-01-01

- ```-e, --stop (required)```:

    **Description**: End date for the report in YYYY-MM-DD format. \
    **Example**: -e 2023-01-31

- ```--api-key (optional)```:

    **Description**: Clockify API key for authentication. If not provided, the default value from settings will be used. \
    **Example**: --api-key your_clockify_api_key

- ```--workspace-id (optional)```:

    **Description**: Clockify workspace ID. If not provided, the default value from settings will be used. \
    **Example**: --workspace-id your_clockify_workspace_id

- ```--google-creds (optional)```:

    **Description**: Path to Google Sheets credentials JSON file. If not provided, the default value from settings will be used. \
    **Example**: --google-creds /path/to/credentials.json

- ```--google-sheet-id (optional)```:

    **Description**: Google Sheet ID to append data to. If not provided, the default value from settings will be used. \
    **Example**: --google-sheet-id your_google_sheet_id

### Configuration Fallback

If optional parameters (--api-key, --workspace-id, --dir_path) are not provided, the package will use the values specified in the 'settings.py' file.