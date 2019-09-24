import numpy as np
import tabulate
from datetime import datetime
from tabulate import _format_table as default_format

from .pretty_array import PrettyArray
from .utils import OrderMatcher, flatten_dict


class PrettyTable:
    """Pretty formatted with order-reflecting colorized columns
    """

    def __init__(self, tablefmt='psql', auto_datetime_fmt='%Y-%m-%d %H:%M:%S', headers=None):
        self.tablefmt = tablefmt
        self.auto_datetime_fmt = auto_datetime_fmt

        self._order_matcher = OrderMatcher()

        self._headers = []
        self._columns = dict()

        tabulate._format_table = self._format_table

    def add_row(self, row):
        row = flatten_dict(row)

        if self.auto_datetime_fmt:
            row = {'dt': str(datetime.now().strftime(self.auto_datetime_fmt)), **row}

        for key in row.keys():
            if key not in self._headers:
                self._headers.append(key)
                guessed_direction = self._order_matcher.predict(key)
                self._columns[key] = PrettyArray(direction=guessed_direction)

        [self._columns[key].add(value) for key, value in row.items()]

    def _format_table(self, fmt, headers, rows, colwidths, colaligns, is_multiline):
        r = default_format(fmt, headers, rows, colwidths, colaligns, is_multiline)
        return r

    def get(self):
        rows = np.array([self._columns[key].get_colorized() for key in self._headers]).T
        t = tabulate.tabulate(rows, headers=self._headers, tablefmt=self.tablefmt)
        return t

    def __str__(self):
        return self.get()
