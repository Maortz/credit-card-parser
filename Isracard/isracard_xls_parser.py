from __future__ import annotations

import datetime
from pathlib import Path
from typing import NamedTuple, List, Tuple, Any

import pandas as pd

from rows import is_empty_cell, is_title_row, is_transaction_heading_row, is_empty_row, is_end_of_transaction_row, \
    is_non_transaction_data_row


class IsracardParser:
    class Transaction(NamedTuple):
        date: datetime.date
        store: str
        transaction_amount: float
        original_currency: str
        billing_amount: float
        billing_currency: str
        voucher_number: int
        details: str

    class CreditCard(NamedTuple):
        last_numbers: int
        credit_type: str
        billing_date: datetime.date
        local_transactions: List[IsracardParser.Transaction]
        overseas_transactions: List[IsracardParser.Transaction]

    class Report(NamedTuple):
        holder: str
        cards: List[IsracardParser.CreditCard]

    class ParserException(ValueError):
        def __init__(self, *args, **kwargs):
            super(IsracardParser.ParserException, self).__init__(args, kwargs)
            self.empty_row = True if kwargs.get('empty_row') else False

    @staticmethod
    def parse_card_details(card_row: Tuple[Any, ...]) -> Tuple[str, int, datetime.date]:
        billing_date = None
        if not is_empty_cell(card_row[2]):
            billing_date = datetime.datetime.strptime(card_row[2], "%d/%m/%y").date()
        card_type, last_numbers = str(card_row[0]).rsplit('-', 1)
        last_numbers = int(last_numbers)
        return card_type, last_numbers, billing_date

    @staticmethod
    def skip_heading_rows(row_iterator) -> None:
        heading_row = next(row_iterator)
        if is_title_row(heading_row):
            heading_row = next(row_iterator)
        if not is_transaction_heading_row(heading_row):
            if is_empty_row(heading_row):
                raise IsracardParser.ParserException(empty_row=True)
            raise IsracardParser.ParserException('Unknown Row')

    @staticmethod
    def parse_holder_row(row_iterator) -> str:
        holder = next(row_iterator)[0]
        next(row_iterator)  # skip separator row
        return holder

    @staticmethod
    def parse_transaction_rows(row_iterator) -> List[Transaction]:
        IsracardParser.skip_heading_rows(row_iterator)
        transactions = list()
        for row in row_iterator:
            if is_end_of_transaction_row(row):
                break
            elif is_non_transaction_data_row(row):
                continue
            transactions.append(IsracardParser.Transaction(*row))
        return transactions

    @staticmethod
    def parse_card(row_iterator) -> CreditCard:
        """
        assume positioned on the card row
        :param row_iterator:
        :return:
        """
        card_row_tuple = next(row_iterator)
        card_type, last_numbers, billing_date = IsracardParser.parse_card_details(card_row_tuple)
        try:
            local_transactions = IsracardParser.parse_transaction_rows(row_iterator)  # locals
            overseas_transactions = IsracardParser.parse_transaction_rows(row_iterator)  # overseas
        except IsracardParser.ParserException as exc:
            if not exc.empty_row:
                raise
            local_transactions = list()
            overseas_transactions = list()
        return IsracardParser.CreditCard(last_numbers=last_numbers, credit_type=card_type, billing_date=billing_date,
                                         local_transactions=local_transactions,
                                         overseas_transactions=overseas_transactions)

    @staticmethod
    def parse_report_file(file_path: Path) -> Report:
        df: pd.DataFrame = pd.read_excel(Path(file_path))
        rows_iterator = df.itertuples(index=False)
        cards = list()
        holder_name = ''
        try:
            holder_name = IsracardParser.parse_holder_row(rows_iterator)
            while True:
                cards.append(IsracardParser.parse_card(rows_iterator))
        except StopIteration:
            pass
        return IsracardParser.Report(holder=holder_name, cards=cards)


if __name__ == '__main__':
    IsracardParser.parse_report_file(Path(r"../Export_7_2021.xls"))
