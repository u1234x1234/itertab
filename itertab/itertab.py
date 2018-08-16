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


TERMINAL = Terminal()
ASC_PATTERN = re.compile('(?=acc)|(?=prec)|(?=recall)|(?=f1)', re.I)
DESC_PATTERN = re.compile('(?=loss)|(?=entropy)|(?=ce)|(?=divergence)', re.I)
CLEAR = '\033[K'


def predict_target_direction(name):
    if ASC_PATTERN.findall(name):
        return 1
    if DESC_PATTERN.findall(name):
        return -1
    return 0


def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield str(key) + '_' + str(subkey), subvalue
            else:
                yield str(key), value

    return dict(items())


def _modify_rows(rows, headers):
    n_columns = len(rows[0])
    n_lines = len(rows)
    assert len(headers) == n_columns

    modified_rows = []
    for col_idx in range(n_columns):
        col = [v[col_idx] for v in rows]
        try:
            float_column = np.array(col, dtype=np.float32)
        except ValueError as e:
            modified_rows.append(col)
            continue

        m_row = [col[0]]
        for i in range(1, len(float_column)):
            is_gt = float_column[i] > float_column[i - 1]
            if isinstance(is_gt, np.ndarray):
                is_gt = is_gt.all()
            direction = predict_target_direction(headers[col_idx])
            value = str(col[i])
            if (is_gt and direction == 1) or (not is_gt and direction == -1):
                value = Fore.GREEN + str(value) + Style.RESET_ALL
            elif (not is_gt and direction == 1) or (is_gt and direction == -1):
                value = Fore.RED + str(value) + Style.RESET_ALL

            m_row.append(value)
        modified_rows.append(m_row)
    rows = list(map(list, zip(*modified_rows)))
    return rows


class Table:
    def __init__(self, auto_datetime_fmt=None):
        self.columns = None
        self.rows = []
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
        rows = _modify_rows(rows, self.columns)
        r = default_format(fmt, headers, rows, colwidths, colaligns, is_multiline)
        return r

    def add_row(self, row):
        row = flatten_dict(row)
        if self.auto_datetime_fmt:
            row = {'dt': str(datetime.now().strftime(self.auto_datetime_fmt)), **row}

        keys, values = list(row.keys()), list(row.values())

        if self.columns is None:
            self.columns = keys
        if len(values) != len(self.columns):
            raise Exception('Number of columns mismatch: {} != {}'.format(len(self.columns), len(values)))

        self.rows.append(values)
        t = tabulate.tabulate(self.rows, headers=self.columns, tablefmt='psql')

    def _print(self):
        if TERMINAL.is_a_tty:
            self.default_stdout_write('\n' + self.get() + '\n' + (TERMINAL.move_up * self.height()) + TERMINAL.move_up)

    def _add_print(self, row):
        self.add_row(row)
        self._print()

    def clear(self):
        self.default_stdout_write(('\n' + CLEAR) * self.height() + TERMINAL.move_up * self.height())

    def _get(self, max_height=None):
        if len(self.rows) == 0:
            return ''
        rows = _modify_rows(self.rows, self.columns)
        if max_height is not None and len(rows) > max_height:
            prefix = rows[:max_height // 2]
            suffix = rows[-max_height // 2:]
            sep = ['...' for r in rows]
            t = prefix + [sep] + suffix
        else:
            t = rows
        t = tabulate.tabulate(t, headers=self.columns, tablefmt='psql')
        return t

    def get(self):
        self.clear()
        return self._get()

    def height(self):
        return len(self._get().split('\n'))

    def to_html():
        pass

    def to_csv(self, path):
        df = pd.DataFrame(self.rows, columns=self.columns)
        df.to_csv(path, index=False)

    def plot():
        pass

    def cleanup(self):
        self.default_stdout_write(TERMINAL.move_down * self.height() + ('\n' + CLEAR))
        sys.stdout.write = self.default_stdout_write
