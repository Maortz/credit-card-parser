import enum
import json
from pathlib import Path
from typing import List, Dict, Tuple, Union

import user_categories


class CategoryClassifier:
    def __init__(self, categories_file: Path, business_to_category_file: Path):
        self._categories_file = categories_file
        self._business_to_category_file = business_to_category_file
        self._read_files()
        self._check_for_mismatch_files()
        self.categories: enum.Enum = enum.Enum("Categories", self.categories_list)

    def _read_files(self):
        with self._categories_file.open(mode='r', encoding='utf-8') as fd:
            self.categories_list: List[str] = json.load(fd)
        with self._business_to_category_file.open(mode='r', encoding='utf-8') as fd:
            self._business_to_category_map: Dict[str, str] = json.load(fd)

    def _write_files(self, write_categories_file: bool, write_business_file: bool):
        if write_categories_file:
            with self._categories_file.open(mode='w', encoding='utf-8') as fd:
                json.dump(self.categories_list, fd, ensure_ascii=False, indent='\t')
        if write_business_file:
            with self._business_to_category_file.open(mode='w', encoding='utf-8') as fd:
                json.dump(self._business_to_category_map, fd, ensure_ascii=False, indent='\t')

    def _check_for_mismatch_files(self) -> None:
        for category in self._business_to_category_map.values():
            if category not in self.categories_list:
                raise Exception()

    def _get_user_category(self, to_business: str) -> Tuple[str, bool]:
        ui = user_categories.TkinterCategoryUI(self)
        return ui.get_user_category_to(to_business)

    def get_category(self, business_name: str, prompt: bool = True) -> enum.Enum:
        category = self._business_to_category_map.get(business_name)
        if category is None and prompt:
            category, repeat = self._get_user_category(business_name)
            if repeat:
                self.add_category(category, business_name)
        return self.categories[category]

    def add_category(self, category: Union[str, List[str]], business_name: str = None) -> None:
        category_updated = False
        if type(category) is list:
            cat_to_add = set(category).difference(self.categories_list)
            category_updated = True if len(cat_to_add) != 0 else False
            self.categories_list.extend(cat_to_add)
        else:
            if category not in self.categories_list:
                self.categories_list.append(category)
                category_updated = True
        business_updated = False
        if business_name is not None:
            self._business_to_category_map[business_name] = category
            business_updated = True
        self._check_for_mismatch_files()
        self._write_files(category_updated, business_updated)
        if category_updated:
            self.categories = enum.Enum("Categories", self.categories_list)
