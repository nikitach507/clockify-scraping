# Reportify

Reportify is a command-line tool designed for extracting and processing time tracking data from Clockify and generating detailed reports in data sheet format. It helps users to easily compile and analyze their project-related time entries over specified periods. This package allows to create reports in data sheets such as Excel and Google Sheet.

With Reportify, you can automate the process of retrieving time logs, formatting them into structured sheets, and generating comprehensive reports for effective time management and project analysis.

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

- **Different type of data sheets**: 

    Creates well-structured Google Sheet or Excel files with detailed tables, including headers, time slots, and user-specific data.

- **Summary and Totals**: 

    Computes and includes summary totals and overall time spent, both daily and for the entire report period.

## Installation and Setup

To set up and start using Reportify, follow these steps:

1. Clone the Repository:

    ```bash
    git clone https://github.com/nikitach507/clockify-scraping.git
    ```

2. Navigate into the project directory:

    ```bash
    cd reportify
    ```

3. Configure the Project:

    Set the required environment variables to match your environment and requirements. You can add these to your shell configuration file (e.g., .bashrc, .zshrc) or set them manually in your terminal.

    ```bash
    export CLOCKIFY_API_KEY='your_clockify_api_key'
    export CLOCKIFY_BASE_URL='https://api.clockify.me/api/v1'
    export CLOCKIFY_WORKSPACE_ID='your_clockify_workspace_id'
    export EXCEL_DIRECTORY='path/to/your/excel/directory'
    export GOOGLE_SHEETS_CREDENTIALS_FILE='path/to/credentials.json'
    export GOOGLE_OAUTH_TOKEN_FILE='path/to/token.json'
    export SPREADSHEET_ID='your_google_spreadsheet_id'
    ```

4. Install the Required Package:

    ```bash
    poetry build
    ```

5. install the package using pip:

    ```bash
    pip install --force-reinstall dist/reportify-0.1.0.tar.gz
    ```

## Configuration

To configure Reportify, set the required environment variables in your system's environment settings. Here are the necessary variables:

1. **Clockify API Key**:

    This is your personal API key for accessing the Clockify API.

    ```bash
    export CLOCKIFY_API_KEY='your_clockify_api_key'
    ```

    > You can obtain your Clockify API key from: Clockify account -> Preferences -> Advanced -> API.

2. **Clockify Base URL**:

    This is the base URL for the Clockify API. Typically, this should not need to be changed.

    ```bash
    export CLOCKIFY_BASE_URL='https://api.clockify.me/api/v1'
    ```

3. **Clockify Workspace ID**:

    This is the ID of the workspace you want to work with in Clockify. Replace the placeholder with your actual workspace ID.

    ```bash
    export CLOCKIFY_WORKSPACE_ID='your_clockify_workspace_id'
    ```

    > You can obtain your Clockify Workspace ID from: Workspaces -> Settings -> Get ID from URL.

4. **Google Sheets Credentials File**:

    This is the path to your Google Sheets credentials JSON file.

    ```bash
    export GOOGLE_SHEETS_CREDENTIALS_FILE='path/to/credentials.json'
    ```

    > You can obtain this file by creating a project in the Google Cloud Console, enabling the Google Sheets API, and generating OAuth 2.0 credentials. Download the JSON file and save it to your preferred directory.

5. **Google OAuth Token File**:

    This is the path to your Google OAuth token JSON file.

    ```bash
    export GOOGLE_OAUTH_TOKEN_FILE='path/to/token.json'
    ```

    > This file is generated the first time you run your application and go through the OAuth flow. The file will be saved automatically in the specified directory.

6. **Google Spreadsheet ID**:

    This is the ID of the Google Spreadsheet you want to append data to.

    ```bash
    export SPREADSHEET_ID='your_google_spreadsheet_id'
    ```

    > You can find the spreadsheet ID in the URL of your Google Sheet. It is the long string between /d/ and /edit.

7. **Excel Directory**: 

    This is the directory where Reportify will save the generated Excel files.

    ```bash
    export EXCEL_DIRECTORY='path/to/your/excel/directory'
    ```

## Package Features

The Reportify package offers the following features and options for generating Excel reports from Clockify data:

### Command-Line Options

- ```-t, --type (required)```:

    **Description**: Type of data sheet to receive the report in. This option should be either `sheet` or `excel`. \
    **Example**: -t excel

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

- ```--dir-path (optional)```:

    **Description**: Directory path where the Excel file will be saved. If not provided, the default value from settings will be used. \
    **Example**: --dir_path /path/to/directory

### Configuration Fallback

If optional parameters (--api-key, --workspace-id, --dir-path, --google-creds, --google-sheet-id) are not provided, the package will use the values specified in the environment variables.
