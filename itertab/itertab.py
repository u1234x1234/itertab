# -*- coding: utf-8 -*-
import atexit
import os
import re
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import tabulate
from blessings import Terminal
from colorama import Back, Fore, Style
from tabulate import _format_table as default_format

from .utils import flatten_dict

TERMINAL = Terminal()

CLEAR = '\033[K'


def _words_matcher(words):
    """Construct a regexp that matches any of `words`
    """
    reg_exp = '|'.join('(?={})'.format(word) for word in words)
    return re.compile(reg_exp, re.I)


class OrderMatcher:
    def __init__(self):
        asc_meanings = ['acc', 'prec', 'recall', 'f1', 'auc']
        desc_meanings = ['loss', 'entropy', 'ce', 'divergence']
        self._asc_pattern_matcher = _words_matcher(asc_meanings)
        self._desc_pattern_matcher = _words_matcher(desc_meanings)

    def predict(self, name):
        """Predict whether the `name` matches ascending or descending orders of improvements
        """
        if self._asc_pattern_matcher.findall(name):
            return 1
        if self._desc_pattern_matcher.findall(name):
            return -1
        return 0


class PrettyTable:
    """Pretty formatted and colorized table 
    """
    def __init__(self):
        self._order_matcher = OrderMatcher()
        self.headers = None
        self.rows = []

    def add_row(self, row):
        row = flatten_dict(row)

        keys, values = list(row.keys()), list(row.values())

        if self.headers is None:
            self.headers = keys
        if len(values) != len(self.headers):
            raise Exception('Number of headers mismatch: {} != {}'.format(len(self.headers), len(values)))

        self.rows.append(values)
        t = tabulate.tabulate(self.rows, headers=self.headers, tablefmt='psql')

    def _colorize_table(self, rows):
        """Add color modifiers to the table cells based on its values and guessed headers meanings
        """
        n_headers = len(rows[0])
        n_lines = len(rows)
        assert len(self.headers) == n_headers

        modified_rows = []
        for col_idx in range(n_headers):
            direction = self._order_matcher.predict(self.headers[col_idx])
            col = [v[col_idx] for v in rows]
            try:
                float_column = np.array(col, dtype=np.float32)
            except ValueError as e:
                modified_rows.append(col)
                continue
            if direction == 0:
                modified_rows.append(col)
                continue

            m_row = [col[0]]
            min_idx = np.argmin(float_column)
            max_idx = np.argmax(float_column)

            for i in range(1, len(float_column)):
                is_gt = float_column[i] > float_column[i - 1]
                if isinstance(is_gt, np.ndarray):
                    is_gt = is_gt.all()

                value = str(col[i])
                fore_modifier = None
                if (is_gt and direction == 1) or (not is_gt and direction == -1):
                    fore_modifier = Fore.GREEN
                elif (not is_gt and direction == 1) or (is_gt and direction == -1):
                    fore_modifier = Fore.RED

                background_modifier = None
                if i == min_idx:
                    background_modifier = Back.RED if direction == 1 else Back.GREEN
                if i == max_idx:
                    background_modifier = Back.GREEN if direction == 1 else Back.RED

                if background_modifier:
                    value = background_modifier + value + Style.RESET_ALL
                    fore_modifier = None

                if fore_modifier:
                    value = fore_modifier + value + Style.RESET_ALL

                m_row.append(value)
            modified_rows.append(m_row)
        rows = list(map(list, zip(*modified_rows)))
        return rows

    def to_csv(self, path):
        df = pd.DataFrame(self.rows, columns=self.headers)
        df.to_csv(path, index=False)

    def _get(self, max_height=None):
        if len(self.rows) == 0:
            return ''
        rows = self._colorize_table(self.rows)
        if max_height is not None and len(rows) > max_height:
            prefix = rows[:max_height // 2]
            suffix = rows[-max_height // 2:]
            sep = ['...' for r in rows]
            t = prefix + [sep] + suffix
        else:
            t = rows
        t = tabulate.tabulate(t, headers=self.headers, tablefmt='psql')
        return t


class Table:
    def __init__(self, auto_datetime_fmt=None):
        self._table = PrettyTable()

        self.auto_datetime_fmt = auto_datetime_fmt
        atexit.register(self.cleanup)
        tabulate._format_table = self._format_table
        self.default_stdout_write = sys.stdout.write
        sys.stdout.write = self.patched_write

    def update(self, row):
        self._add_print(row)

    def patched_write(self, q):
        if TERMINAL.is_a_tty:
            self.default_stdout_write(q + CLEAR)
            tt = self.get()
            self.default_stdout_write('\n' + tt + '\n' + (TERMINAL.move_up * self.height()) + TERMINAL.move_up)
        else:
            self.default_stdout_write(q)

    def _format_table(self, fmt, headers, rows, colwidths, colaligns, is_multiline):
        rows = self._table._colorize_table(rows)
        r = default_format(fmt, headers, rows, colwidths, colaligns, is_multiline)
        return r

    def _print(self):
        if TERMINAL.is_a_tty:
            self.default_stdout_write('\n' + self.get() + '\n' + (TERMINAL.move_up * self.height()) + TERMINAL.move_up)

    def _add_print(self, row):
        self.add_row(row)
        self._print()

    def clear(self):
        self.default_stdout_write(('\n' + CLEAR) * self.height() + TERMINAL.move_up * self.height())

    def add_row(self, row):
        if self.auto_datetime_fmt:
            row = {'dt': str(datetime.now().strftime(self.auto_datetime_fmt)), **row}

        self._table.add_row(row)

    def get(self):
        self.clear()
        return self._table._get()

    def height(self):
        return len(self._table._get().split('\n'))

    def to_csv(self, filename):
        self._table.to_csv(filename)

    def to_html():
        pass

    def plot():
        pass

    def cleanup(self):
        self.default_stdout_write(TERMINAL.move_down * self.height() + ('\n' + CLEAR))
        sys.stdout.write = self.default_stdout_write
