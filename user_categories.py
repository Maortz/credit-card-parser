import abc
import tkinter
from functools import partial
from typing import Tuple


class CategoriesUI(abc.ABC):
    def __init__(self, classifier):
        self._classifier = classifier

    def get_user_category_to(self, business: str) -> Tuple[str, bool]:
        pass


class CmdCategoryUI(CategoriesUI):
    def __init__(self, classifier):
        super().__init__(classifier)

    def get_user_category_to(self, business: str) -> Tuple[str, bool]:
        all_cat = ('{}\n' * len(self._classifier.categories_list)).format(
            *(f'{i}. {c}' for i, c in enumerate(self._classifier.categories_list, start=1)))
        category = input(
            f"Please enter new category or select one of the following: \n{all_cat}\n"
            f"* add prefix '-' for non-repeat transaction\n"
            f"* {self._classifier.categories_list.index('unknown') + 1} for unknown transaction\n"
            f"for:\n\t{business}\n>")
        repeat = True
        if category[0] == '-':
            repeat = False
            category = category[1:]
        category = self._get_category_from_index(category)
        return category, repeat

    def _get_category_from_index(self, category_index: str) -> str:
        try:
            idx = int(category_index)
        except ValueError:  # new category
            return category_index
        return self._classifier.categories(idx).name


class TkinterCategoryUI(CategoriesUI):
    def __init__(self, classifier):
        super().__init__(classifier)
        self.result = None

    def handle_button_click(self, root: tkinter.Tk, category: str, is_repeat: tkinter.IntVar) -> None:
        self.result = category, not bool(is_repeat.get())
        root.destroy()

    def get_user_category_to(self, business: str) -> Tuple[str, bool]:
        window = tkinter.Tk()
        window.title('Choose Category')
        tkinter.Label(window, text=business).grid(column=0, row=0, columnspan=2)
        checkbox_vars = [tkinter.IntVar() for i in self._classifier.categories_list]
        checkboxes = [tkinter.Checkbutton(window, text='classify only once', variable=v).grid(column=1, row=i) for
                      i, v in enumerate(checkbox_vars, 1)]
        [tkinter.Button(window, text=category,
                        command=partial(self.handle_button_click, window, category, checkbox_vars[i])).grid(
            column=0,
            row=i + 1,
            sticky="news")
            for
            i, category in enumerate(self._classifier.categories_list)]
        window.mainloop()
        if self.result is None:
            raise RuntimeError()
        return self.result
