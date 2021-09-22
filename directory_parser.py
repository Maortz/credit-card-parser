import datetime
import enum
from pathlib import Path
from typing import List, Optional, NamedTuple, Callable, Dict, Union

from Isracard.isracard_xls_parser import IsracardParser
from category_classifier import CategoryClassifier


class MonthAtYear:
    def __new__(cls, date: Union[datetime.date, str]):
        if not hasattr(cls, 'container'):
            cls.container = dict()
        if type(date) is str:
            date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        if (date.year, date.month) not in cls.container:
            cls.container[(date.year, date.month)] = object.__new__(cls)
        return cls.container[(date.year, date.month)]

    def __init__(self, date: Union[datetime.date, str]):
        if type(date) is str:
            date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        self.year = date.year
        self.month = date.month

    def __str__(self):
        return f'{self.month}/{self.year}'


class Transaction(NamedTuple):
    transaction_details: IsracardParser.Transaction
    holder: str
    category: enum.Enum


MonthOnCategoryDict = Dict[MonthAtYear, Dict[enum.Enum, float]]


class HolderTransactions:
    def __init__(self, classifier: CategoryClassifier, *, transaction: Optional[List[Transaction]] = None,
                 directory_to_parse: Optional[Path] = None):
        if transaction is not list or type(transaction[0]) is not Transaction:
            transaction = list()
        self._transactions = transaction
        if directory_to_parse is not None:
            self._transactions.extend(
                HolderTransactions.gets_transaction_from_directory(directory_to_parse,
                                                                   classifier))

    def get_months(self) -> List[MonthAtYear]:
        return list(dict.fromkeys(sorted((MonthAtYear(tr.transaction_details.date) for tr in self._transactions),
                                         key=lambda date: int(f'{date.year}{date.month}'))))

    def get_transactions_dict(self) -> MonthOnCategoryDict:
        all_time_dict: Dict[MonthAtYear, Dict[enum.Enum, float]] = dict()
        for transaction in self._transactions:
            month = MonthAtYear(transaction.transaction_details.date)
            if month not in all_time_dict:
                all_time_dict[month]: Dict[enum.Enum, float] = dict()
            month_dict = all_time_dict[month]
            if transaction.category not in month_dict:
                month_dict[transaction.category] = 0.0
            month_dict[transaction.category] += transaction.transaction_details.billing_amount
        return all_time_dict

    def add_transactions(self, transactions: List[Transaction]) -> None:
        if len(transactions) > 0 and type(transactions[0]) is not Transaction:
            raise TypeError()
        self._transactions.extend(transactions)

    def get_transactions_by_month(self, month: MonthAtYear) -> List[Transaction]:
        return [transaction for transaction in self._transactions if
                MonthAtYear(transaction.transaction_details.date) is month]

    def get_transactions_by_category(self, category: enum.Enum) -> List[Transaction]:
        return [transaction for transaction in self._transactions if
                transaction.category is category]

    def get_transactions_if(self, cond: Callable[[Transaction], bool]):
        return [transaction for transaction in self._transactions if
                cond(transaction)]

    @staticmethod
    def gets_transaction_from_directory(root_dir: Path, classifier: CategoryClassifier) -> List[Transaction]:
        report_list: List[IsracardParser.Report] = [
            IsracardParser.parse_report_file(file) for file in
            root_dir.glob('*.xls')]
        transactions_list: List[Transaction] = list()
        for holder, cards in report_list:
            for card in cards:
                transactions_list.extend(
                    [Transaction(transaction, holder, classifier.get_category(transaction.business_name)) for
                     transaction in card.local_transactions])
                transactions_list.extend(
                    [Transaction(transaction, holder, classifier.get_category(transaction.business_name)) for
                     transaction in card.overseas_transactions])
        return transactions_list
