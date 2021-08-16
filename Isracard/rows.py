import math


def is_empty_cell(pandas_cell) -> bool:
    return type(pandas_cell) is float and math.isnan(pandas_cell)


def is_empty_row(pandas_row) -> bool:
    return all((is_empty_cell(cell) for cell in pandas_row))


def is_title_row(pandas_row) -> bool:
    return not is_empty_cell(pandas_row[0]) and all((is_empty_cell(cell) for cell in pandas_row[1:]))


def is_transaction_heading_row(pandas_row) -> bool:
    # overseas heading is 1 less
    return all((type(cell) is str for cell in pandas_row[:-1]))


def is_non_transaction_data_row(pandas_row) -> bool:
    return any((is_empty_cell(cell) for cell in pandas_row[:-1]))


def is_end_of_transaction_row(pandas_row) -> bool:
    return all((is_empty_cell(cell) for cell in pandas_row[1:-1]))
