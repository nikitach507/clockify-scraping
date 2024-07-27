# Excelify

Excelify is a command-line tool designed for extracting and processing time tracking data from Clockify and generating detailed Excel reports. It helps users to easily compile and analyze their project-related time entries over specified periods.

With Excelify, you can automate the process of retrieving time logs, formatting them into structured Excel sheets, and generating comprehensive reports for effective time management and project analysis.

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

- **Excel Report Generation**: 

    Creates well-structured Excel files with detailed tables, including headers, time slots, and user-specific data.

- **Summary and Totals**: 

    Computes and includes summary totals and overall time spent, both daily and for the entire report period.

## Installation and Setup

To set up and start using Excelify, follow these steps:

1. Clone the Repository:

    ```sh
    git clone https://github.com/nikitach507/clockify-scraping.git
    ```

2. Navigate into the project directory:

    ```sh
    cd clockify-scraping
    ```

3. Configure the Project:
Update the configuration settings to match your environment and requirements.

    ```sh
    nano excelify/config/settings.py
    ```

4. Install the Required Package:

    ```sh
    poetry build
    ```

5. install the package using pip:

    ```sh
    pip install --force-reinstall dist/excelify-0.1.0.tar.gz
    ```

## Configuration

To configure Excelify, you need to update the settings in the `settings.py` file located in the `config` directory. The following parameters must be set:

1. **Workspace Name**

    This optional parameter allows you to include a specific name for the workspace in the generated Excel reports. If not set, a default label will be used.

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

5. **Excel Directory**: 

    This is the directory where Excelify will save the generated Excel files.

    ```python
    EXCEL_DIRECTORY = 'path/to/your/excel/directory'
    ```

## Package Features

The Excelify package offers the following features and options for generating Excel reports from Clockify data:

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

- ```--dir_path (optional)```:

    **Description**: Directory path where the Excel file will be saved. If not provided, the default value from settings will be used. \
    **Example**: --dir_path /path/to/directory

### Configuration Fallback

If optional parameters (--api-key, --workspace-id, --dir_path) are not provided, the package will use the values specified in the 'settings.py' file.

## Lisense

MIT License

Copyright (c) 2024 [Nikita Chuprin]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
