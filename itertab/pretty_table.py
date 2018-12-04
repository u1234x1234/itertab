import numpy as np
import pandas as pd
import tabulate
from colorama import Back, Fore, Style
from tabulate import _format_table as default_format
from collections import namedtuple
from collections import defaultdict

from .utils import flatten_dict, OrderMatcher


class OrderableArray:
    def __init__(self, direction: str, len: int=0):
        if direction not in {-1, 0, 1}:
            raise ValueError('Direction not in {-1, 0, 1}')

        self.direction = direction

        self._raw_values = [None for _ in range(len)]
        self._mask = [0 for _ in range(len)]

        self._min_idx = None
        self._min_val = np.inf

        self._max_idx = None
        self._max_val = -np.inf

    def add(self, value):
        try:
            float_value = float(value)
            order = (float_value > float(self._raw_values[-1])) * 2 - 1  # map to {-1, 1}
            order *= self.direction
            if float_value < self._min_val:
                self._min_val = float_value
                self._min_idx = len(self._raw_values) + 1
            if float_value > self._max_val:
                self._max_val = float_value
                self._max_idx = len(self._raw_values) + 1
        except:
            order = 0

        self._raw_values.append(str(value))
        self._mask.append(order)

    def get_colorized(self, highlight_min=True, highlight_max=True):
        colorized_array = []
        modifiers_map = {
            1: Fore.GREEN,
            -1: Fore.RED,
        }
        colorized_array = []
        for val, fl in zip(self._raw_values, self._mask):
            if fl in modifiers_map:
                colorized_array.append(modifiers_map[fl] + val + Style.RESET_ALL)
            else:
                colorized_array.append(val)

        return colorized_array


class PrettyTable:
    """Pretty formatted and colorized table 
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
                self._columns[key] = Array(self._order_matcher.predict(key))

        [self._columns[key].add(value) for key, value in row.items()]

    def _format_table(self, fmt, headers, rows, colwidths, colaligns, is_multiline):
        r = default_format(fmt, headers, rows, colwidths, colaligns, is_multiline)
        return r

    def get(self):
        rows = np.array([self._columns[key].get_colorized() for key in self._headers]).T
        t = tabulate.tabulate(rows, headers=self._headers, tablefmt=self.tablefmt)
        return t
