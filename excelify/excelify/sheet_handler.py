from datetime import datetime, timedelta
from xlsxwriter import Workbook, utility
import calendar


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

def generate_all_totals(number_users: int, num_days: int, start_date: str, stop_date: str) -> tuple[list[str], list[dict[int, str]]]:
    total_row_end = num_days * 99 + 1
    all_total_formula_row = []
    all_buffers_rows = []

    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    column_letters = [utility.xl_col_to_name(idx) for idx in range(1, number_users + 1)]

    for column_letter in column_letters:
        buffer_rows, buffer_minutes_formula = [], []
        current_date = start_datetime
        fixed_year, fixed_month = current_date.year, current_date.month

        for iteration in range(100, total_row_end + 1, 99):
            if fixed_month < current_date.month or fixed_year < current_date.year:
                buffer_rows.append(f"=TEXT(INT(({'+'.join(buffer_minutes_formula)}) / 60), \"0\") & \":\" & TEXT(MOD(({'+'.join(buffer_minutes_formula)}), 60), \"00\")")
                buffer_minutes_formula.clear()
                fixed_month, fixed_year = current_date.month, current_date.year

            buffer_minutes_formula.append(f"HOUR(TIMEVALUE({column_letter}{iteration}))*60+MINUTE(TIMEVALUE({column_letter}{iteration}))")
            current_date += timedelta(days=1)

        buffer_rows.append(f"=TEXT(INT(({'+'.join(buffer_minutes_formula)}) / 60), \"0\") & \":\" & TEXT(MOD(({'+'.join(buffer_minutes_formula)}), 60), \"00\")")
        
        join_buffer_cell = '+'.join(
            [f"LEFT({column_letter}{total_row_end + idx + 3},FIND(\":\",{column_letter}{total_row_end + idx + 3})-1)*60+"
             f"RIGHT({column_letter}{total_row_end + idx + 3},LEN({column_letter}{total_row_end + idx + 3})-FIND(\":\",{column_letter}{total_row_end + idx + 3}))" 
            for idx in range(len(buffer_rows))]
        )

        all_total_formula_row.append(f"=TEXT(INT(({join_buffer_cell}) / 60), \"0\") & \":\" & TEXT(MOD(({join_buffer_cell}), 60), \"00\")")
        all_buffers_rows.append({idx: row for idx, row in enumerate(buffer_rows)})

    all_total_row = [f'{start_date} / {stop_date}'] + all_total_formula_row

    return all_total_row, all_buffers_rows
    
def append_data_to_sheet(worksheet,  workbook: Workbook, data: list, current_date: str, users_in_work: int, start_row: int) -> None:
    format_special_cell = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True})
    format_small_fill = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'border': 1})
    format_description = workbook.add_format({'align': 'fill', 'valign': 'vcenter', 'border': 1, 'text_wrap': False, 'shrink': True})
    format_total = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': 'D9D9D9', 'border': 1, 'bold': True})

    row_index = start_row + 99

    for row_idx, row in enumerate(data):
        row_format = [format_small_fill if not cell else format_special_cell 
                                        if col == 0 or row_idx == 0 else format_small_fill 
                                        if len(cell) <= 10 else format_description 
                                        for col, cell in enumerate(row)]
        
        for col_index, (cell_value, format_row) in enumerate(zip(row, row_format)):
            worksheet.write(start_row + row_idx, col_index, cell_value, format_row)

    total_rows = generate_total_rows(current_date, start_row + 2, users_in_work)
    for col_index, cell_value in enumerate(total_rows):
        worksheet.write(row_index - 2, col_index, cell_value, format_total)
    
    worksheet.write(row_index - 1, 0, "")

def append_all_totals(worksheet, workbook: Workbook, num_days: int, active_users_name: list, start_row: int, start_date: str, stop_date: str) -> None:
    format_total_name = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'border': 1, 'bg_color': 'DDD9C4', 'bold': True})
    format_all_total = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': 'DDD9C4', 'border': 1, 'bold': True})
    format_buffer_name = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'border': 1, 'bold': True})
    format_buffer = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True})

    all_totals, all_buffer = generate_all_totals(len(active_users_name), num_days, start_date, stop_date)

    header_row = ["ALL TOTAL"] + active_users_name
    worksheet.write_row(start_row - 1, 0, header_row, format_all_total)

    for col, value in enumerate(all_totals):
        cell_format = format_total_name if col == 0 else format_all_total
        worksheet.write(start_row, col, value, cell_format)
    
    start_row += 1

    num_buffers = max(len(buffer_dict) for buffer_dict in all_buffer)

    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    stop_datetime = datetime.strptime(stop_date, '%Y-%m-%d')
    current_year = start_datetime.year
    start_month = start_datetime.month

    for number in range(num_buffers):

        current_month = (start_month + number - 1) % 12 + 1
        current_year = start_datetime.year + (start_month + number - 1) // 12

        first_day_month = f"{start_datetime.day:02d}" if start_datetime.month == current_month else "01"
        last_day_month = f"{stop_datetime.day:02d}" if stop_datetime.month == current_month else f"{calendar.monthrange(current_year, current_month)[1]:02d}"

        buffer_row = [f"{current_year}, {calendar.month_name[current_month]} {first_day_month}-{last_day_month}"] + [buffer.get(number, "") for buffer in all_buffer]

        for col, value in enumerate(buffer_row):
            cell_format = format_buffer_name if col == 0 else format_buffer
            worksheet.write(start_row + number, col, value, cell_format)
