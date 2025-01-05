# Clockify Reporting Tools

**Clockify Reporting Tools** is a collection of specialized command-line utilities designed to automate the extraction and **reporting of time-tracking data from Clockify**. Each tool in this repository focuses on a distinct reporting format, offering tailored solutions for creating reports in **Excel, Google Sheets, or both**.

## Overview

This repository contains three independent tools, each targeting a specific type of reporting need:

- **Excelify**: Generate detailed Excel reports from Clockify data. [Excelify README](/excelify/README.md)
- **Reportify**: Create flexible reports in both Excel and Google Sheets formats. [Reportify README](/reportify/README.md)
- **Sheetify**: Directly generate and update Google Sheets with Clockify data. [Sheetify README](/sheetify/README.md)

Each tool operates independently, with its own configuration and setup instructions, found in their respective directories.

## Repository Structure

```sh
.
├── excelify/       # Excel-focused reporting tool
├── reportify/      # Dual-purpose reporting tool for Excel and Google Sheets
├── sheetify/       # Google Sheets-focused reporting tool
└── README.md       # This file
```
## Quick Start

To get started with the **Clockify Reporting Tools**, follow these steps:

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/clockify-reporting-tools.git
    ```

2. Navigate to the desired tool:

    - For **Excelify**: `cd clockify-reporting-tools/excelify`
    - For **Reportify**: `cd clockify-reporting-tools/reportify`
    - For **Sheetify**: `cd clockify-reporting-tools/sheetify`

3. Follow the tool-specific instructions:

    > [!TIP]
    > Each tool has its own README.md file with detailed installation and configuration steps. Open the respective README.md file for the tool you're using to get started.

## Choosing the Right Tool

- **Excelify**: Best for users who require detailed time-tracking reports in Excel format.
- **Reportify**: Ideal for users who need the flexibility to generate reports in both Excel and Google Sheets formats.
- **Sheetify**: Perfect for users who work primarily with Google Sheets for real-time collaboration.
