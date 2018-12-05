import numpy as np
import pandas as pd
import tabulate

from tabulate import _format_table as default_format
from .utils import flatten_dict, OrderMatcher
from .orderable_array import OrderableArray


class PrettyTable:
    """Pretty formatted with order-reflecting colorized columns
    """
    def __init__(self, tablefmt='psql'):
        self.tablefmt = tablefmt

        self._order_matcher = OrderMatcher()

        self._headers = []
        self._columns = dict()

        tabulate._format_table = self._format_table

    def add_row(self, row):
        row = flatten_dict(row)

        for key in row.keys():
            if key not in self._headers:
                self._headers.append(key)
                self._columns[key] = OrderableArray(self._order_matcher.predict(key))

        [self._columns[key].add(value) for key, value in row.items()]

    def _format_table(self, fmt, headers, rows, colwidths, colaligns, is_multiline):
        r = default_format(fmt, headers, rows, colwidths, colaligns, is_multiline)
        return r

    def get(self):
        rows = np.array([self._columns[key].get_colorized() for key in self._headers]).T
        t = tabulate.tabulate(rows, headers=self._headers, tablefmt=self.tablefmt)
        return t
