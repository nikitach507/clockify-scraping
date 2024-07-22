from datetime import datetime
from xlsxwriter import Workbook, utility


def set_column_widths(worksheet, max_col, widths):
    for col in range(max_col):
        worksheet.set_column(col, col, widths.get(col + 1, 20))

def generate_total_rows(current_date: str, start_row: int, number_users: int, num_rows: int = 96) -> list[list[str]]:
    total_formula_row = []
    for col_index in range(2, number_users + 2):
        column_letter = utility.xl_col_to_name(col_index - 1)
        count_formula = f"COUNTIF({column_letter}{start_row}:{column_letter}{start_row + num_rows - 1}, \"<>\")"
        total_minutes = f"{count_formula} * 15"
        formatted_time_formula = f"=TEXT(INT({total_minutes} / 60), \"0\") & \":\" & TEXT(MOD({total_minutes}, 60), \"00\")"
        total_formula_row.append(formatted_time_formula)

    return [f'TOTAL [{current_date}]'] + total_formula_row

def generate_all_totals(number_users: int, num_days: int, start_date: str, stop_date: str) -> tuple[list[list[str]], list[list[int, str]]]:
    total_row_end = num_days * 99 - 1
    all_total_formula_row = []
    all_buffers_rows = []

    for col_index in range(2, number_users + 2):
        column_letter = utility.xl_col_to_name(col_index - 1)
        buffer_rows = []
        total_minutes = "="
        buffer_30_days = 0
        iteration = 98

        while iteration <= total_row_end:
            formula = f"HOUR(TIMEVALUE({column_letter}{iteration}))*60+MINUTE(TIMEVALUE({column_letter}{iteration}))"
            total_minutes += formula + "+"
            buffer_30_days += 1

            if buffer_30_days >= 60:
                buffer_rows.append(total_minutes.rstrip("+"))
                total_minutes = "="
                buffer_30_days = 0

            iteration += 99

        if total_minutes:
            buffer_rows.append(total_minutes.rstrip("+"))

        join_minutes = "+".join(f"{column_letter}{total_row_end + idx + 2 + 2}" for idx in range(len(buffer_rows)))
        total_formula = f"=TEXT(INT(({join_minutes}) / 60), \"0\") & \":\" & TEXT(MOD(({join_minutes}), 60), \"00\")"
        all_total_formula_row.append(total_formula)

        buffer_dict = {idx: row for idx, row in enumerate(buffer_rows)}
        all_buffers_rows.append(buffer_dict)

    all_total_row = [f'ALL TOTAL [{start_date} / {stop_date}]'] + all_total_formula_row

    return all_total_row, all_buffers_rows
    
def append_data_to_sheet(worksheet,  workbook: Workbook, data: list, current_date: str, users_in_work: int, start_row: int) -> None:
    row_index = start_row + 99

    format_special_cell = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
    format_description = workbook.add_format({'align': 'fill', 'valign': 'vcenter', 'border': 1, 'text_wrap': False, 'shrink': True})
    format_total_a = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bg_color': 'D9D9D9', 'border': 1, 'shrink': True})
    format_total = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': 'D9D9D9', 'border': 1})

    for row_idx, row in enumerate(data):
        for col_index, cell_value in enumerate(row):
            format_row = format_special_cell if not cell_value or col_index == 0 or row_idx == 0 else format_description
            worksheet.write(start_row + row_idx, col_index, cell_value, format_row)

    total_rows = generate_total_rows(current_date, start_row + 2, users_in_work)
    for col_index, cell_value in enumerate(total_rows):
        format_row = format_total_a if col_index == 0 else format_total
        worksheet.write(row_index - 2, col_index, cell_value, format_row)
    
    worksheet.write(row_index - 1, 0, "·")

def append_all_totals(worksheet, workbook: Workbook, num_days: int, number_users: int, start_row: int, start_date: datetime, stop_date: datetime) -> None:
    all_totals, all_buffer = generate_all_totals(number_users, num_days, start_date, stop_date)

    format_name_total = workbook.add_format({'align': 'left', 'valign': 'center', 'bg_color': 'DDD9C4', 'border': 1, 'text_wrap': True})
    format_all_total = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': 'DDD9C4', 'border': 1})
    format_buffer = workbook.add_format({'align': 'center', 'valign': 'center', 'border': 0})

    for col_index, cell_value in enumerate(all_totals):
        format_row = format_name_total if col_index == 0 else format_all_total
        worksheet.write(start_row, col_index, cell_value, format_row)
    
    start_row += 1
    worksheet.write_row(start_row, 0, ["·"])
    start_row += 1

    num_buffers = max(len(buffer_dict) for buffer_dict in all_buffer)
    for number in range(num_buffers):
        buffer_row = ["Buffer 60 days"] + [buffer.get(number, "") for buffer in all_buffer]
        worksheet.write_row(start_row + number, 0, buffer_row, format_buffer)
    