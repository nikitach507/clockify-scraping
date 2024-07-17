import re
import click
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


def generate_total_rows(current_date: str, start_row: int, found_users: dict[str, str], num_rows: int = 96) -> list[list[str]]:
    total_formula_row = []
    for col_index, user in enumerate(found_users.values(), start=2): 
        column_letter = get_column_letter(col_index)

        count_formula = f"COUNTIF({column_letter}{start_row}:{column_letter}{start_row + num_rows - 1}, \"<>\")"
        total_minutes = f"{count_formula} * 15"
        formatted_time_formula = f"=TEXT(INT({total_minutes} / 60), \"0\") & \":\" & TEXT(MOD({total_minutes}, 60), \"00\")"
        total_formula_row.append(formatted_time_formula)

    total_row = [f'TOTAL [{current_date}]'] + total_formula_row
    return [total_row]

def append_data_to_sheet(worksheet: Worksheet, data: list[list[str]], current_date: str, found_users: dict[str, str], start_row: int) -> None:
    for row in data:
        worksheet.append(row)

    total_rows = generate_total_rows(current_date, start_row, found_users)
    for total_row in total_rows:
        worksheet.append(total_row)

def generate_all_totals(found_users: dict[str, str], num_days: int, start_date: str, stop_date: str) -> list[list[str]]:
    total_row_end = num_days + num_days * 97
    iteration = 98

    all_total_formula_row = []
    for col_index, user in enumerate(found_users.values(), start=2):
        column_letter = get_column_letter(col_index)
        total_minutes = ""
        while iteration <= total_row_end:
            formula = f"HOUR(TIMEVALUE({column_letter}{iteration}))*60+MINUTE(TIMEVALUE({column_letter}{iteration}))"
            total_minutes += formula
            if iteration != total_row_end:
                total_minutes = total_minutes + "+"
            iteration += 98
        
        total_formula = f"=TEXT(INT(({total_minutes}) / 60), \"0\") & \":\" & TEXT(MOD(({total_minutes}), 60), \"00\")"
        all_total_formula_row.append(total_formula)
        iteration = 98

    all_total_row = [f'ALL TOTAL [{start_date} / {stop_date}]'] + all_total_formula_row
    separator_row = ['-' * 20] * len(all_total_row)
    return [separator_row, all_total_row, separator_row]
    

def append_all_totals(worksheet: Worksheet, num_days: int, found_users: dict[str, str], start_date: str, stop_date: str) -> None:
    all_totals = generate_all_totals(found_users, num_days, start_date, stop_date)
    for row in all_totals:
        worksheet.append(row)
