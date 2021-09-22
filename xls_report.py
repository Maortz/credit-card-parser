from pathlib import Path
import tkinter
import pandas as pd
from numpy.typing import ArrayLike

from category_classifier import CategoryClassifier
from directory_parser import HolderTransactions, MonthOnCategoryDict


class XlsxReporter:
    def __init__(self, configuration_directory: Path = Path('.'), engine: str = 'xlsxwriter'):
        self.xlsx_engine = engine
        self.classifier = CategoryClassifier(configuration_directory / Path('categories.json'),
                                             configuration_directory / Path('categories_mapping.json'))

    def _remove_enum_prefix_from_rows(self, df: pd.DataFrame) -> None:
        df.set_axis(self.classifier.categories_list, axis='rows', inplace=True)

    def _restore_enum_rows(self, df: pd.DataFrame) -> None:
        row_header = [self.classifier.categories[item] for item in df.index.values]
        df.set_axis(row_header, axis='rows', inplace=True)

    def _update_categories_by(self, values_array: ArrayLike) -> None:
        new_categories = list(values_array)
        self.classifier.add_category(new_categories)

    def save_xlsx(self, df: pd.DataFrame, out_xlsx_file: Path):
        self._remove_enum_prefix_from_rows(df)
        df.to_excel(out_xlsx_file, engine=self.xlsx_engine)

    def create_xlsx_report_for_directory(self, directory: Path, out_xlsx_file: Path) -> MonthOnCategoryDict:
        # set DataFrame
        holder = HolderTransactions(self.classifier, directory_to_parse=directory)
        rows_header = self.classifier.categories
        cols_header = holder.get_months()
        table_data: MonthOnCategoryDict = holder.get_transactions_dict()
        df = pd.DataFrame(table_data, index=rows_header, columns=cols_header)
        df.fillna(0, inplace=True)

        # create file
        if out_xlsx_file.is_file():
            df = self.merge_reports(self.load_xlsx_report(out_xlsx_file), df)
            out_xlsx_file.unlink()
        self.save_xlsx(df, out_xlsx_file)
        return table_data

    def load_xlsx_report(self, report_file: Path) -> MonthOnCategoryDict:
        df: pd.DataFrame = pd.read_excel(report_file, index_col=0, header=0)
        df.fillna(0, inplace=True)
        self._update_categories_by(df.index.values)
        self._restore_enum_rows(df)
        return df.to_dict()

    def merge_reports(self, first: MonthOnCategoryDict, second: MonthOnCategoryDict) -> MonthOnCategoryDict:
        raise NotImplementedError()


XlsxReporter().create_xlsx_report_for_directory(Path('.'), Path('../my_excel.xlsx'))
# XlsxReporter().load_xlsx_report(Path('../my_excel.xlsx'))