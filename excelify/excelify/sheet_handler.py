from excelify.table_formating import apply_styles, set_column_widths
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

    
def generate_total_rows(current_date: str, start_row: int, number_users: int, num_rows: int = 96) -> list[list[str]]:
    total_formula_row = []
    for col_index in range(2, number_users + 2):
        column_letter = get_column_letter(col_index)
        count_formula = f"COUNTIF({column_letter}{start_row}:{column_letter}{start_row + num_rows - 1}, \"<>\")"
        total_minutes = f"{count_formula} * 15"
        formatted_time_formula = f"=TEXT(INT({total_minutes} / 60), \"0\") & \":\" & TEXT(MOD({total_minutes}, 60), \"00\")"
        total_formula_row.append(formatted_time_formula)

    return [[f'TOTAL [{current_date}]'] + total_formula_row]

def generate_all_totals(number_users: int, num_days: int, start_date: str, stop_date: str) -> tuple[list[list[str]], list[list[int, str]]]:
    total_row_end = num_days * 99 - 1
    all_total_formula_row = []
    all_buffers_rows = []

    for col_index in range(2, number_users + 2):
        column_letter = get_column_letter(col_index)
        buffer_rows = []
        total_minutes = ""
        buffer_30_days = 0
        iteration = 98

        while iteration <= total_row_end:
            formula = f"HOUR(TIMEVALUE({column_letter}{iteration}))*60+MINUTE(TIMEVALUE({column_letter}{iteration}))"
            total_minutes += formula + "+"
            buffer_30_days += 1

            if buffer_30_days >= 60:
                buffer_rows.append(total_minutes.rstrip("+"))
                total_minutes = ""
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

    return [all_total_row], all_buffers_rows
    
def append_data_to_sheet(worksheet: Worksheet, data: list[list[str]], current_date: str, number_users: int, start_row: int) -> None:
    for row in data:
        worksheet.append(row)
    
    total_rows = generate_total_rows(current_date, start_row, number_users)
    for total_row in total_rows:
        worksheet.append(total_row)
    
    apply_styles(worksheet, min_row=worksheet.max_row, max_row=worksheet.max_row, min_col=1, max_col=number_users + 1, 
                 fill_color="D9D9D9", horizontal_alignment='center', vertical_alignment='center')

    apply_styles(worksheet, min_row=start_row - 1, max_row=worksheet.max_row - 1, min_col=1, max_col=number_users + 1)
    set_column_widths(worksheet=worksheet, max_col=number_users + 1)

def append_all_totals(worksheet: Worksheet, num_days: int, number_users: int, start_date: str, stop_date: str) -> None:
    all_totals, all_buffer = generate_all_totals(number_users, num_days, start_date, stop_date)

    for row in all_totals:
        worksheet.append(row)

    apply_styles(worksheet, min_row=worksheet.max_row, max_row=worksheet.max_row, min_col=1, max_col=number_users + 1,
                 fill_color="DDD9C4", horizontal_alignment='center', vertical_alignment='center')

    worksheet.append(["·"])
    num_buffers = max(len(buffer_dict) for buffer_dict in all_buffer)
    for number in range(num_buffers):
        buffer_row = ["Buffer 60 days"]
        for buffer in all_buffer:
            buffer_value = buffer.get(number, "")
            buffer_row.append(f"={buffer_value}" if buffer_value else "")
        worksheet.append(buffer_row)

    apply_styles(worksheet, min_row=worksheet.max_row - num_buffers, max_row=worksheet.max_row, min_col=1, max_col=number_users + 1,
                 horizontal_alignment='center', vertical_alignment='center', border=None)
