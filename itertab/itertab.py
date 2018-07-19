# -*- coding: utf-8 -*-
import atexit
import os
import re
import sys

import numpy as np
import tabulate
from blessings import Terminal
from colorama import Back, Fore, Style
from tabulate import _format_table as default_format


TERMINAL = Terminal()
ASC_PATTERN = re.compile('(Acc)|(Prec)', re.I)
DESC_PATTERN = re.compile('(Logloss)|(entropy)|(ce)', re.I)


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
                    yield key + '_' + subkey, subvalue
            else:
                yield key, value

    return dict(items())


class Table:
    def __init__(self):
        self.columns = None
        self.rows = []
        self.prev = ''
        atexit.register(self.cleanup)
        tabulate._format_table = self._format_table
        self.default_stdout_write = sys.stdout.write
        sys.stdout.write = self.patched_write

    def patched_write(self, q):
        if TERMINAL.is_a_tty:
            self.default_stdout_write(q + '\033[K')
            tt = self.get()
            self.default_stdout_write('\n' + tt + '\n' + (TERMINAL.move_up * self.height()) + TERMINAL.move_up)
        else:
            self.default_stdout_write(q)

    def _format_table(self, fmt, headers, rows, colwidths, colaligns, is_multiline):
        n_columns = len(rows[0])
        n_lines = len(rows)

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
                direction = predict_target_direction(self.columns[col_idx])
                if (is_gt and direction == 1) or (not is_gt and direction == -1):  # TODO ==
                    color = Fore.GREEN
                else:
                    color = Fore.RED
                if direction == 0:
                    color = Fore.WHITE

                m_row.append(color + col[i] + Style.RESET_ALL)
            modified_rows.append(m_row)
        rows = list(map(list, zip(*modified_rows)))
        r = default_format(fmt, headers, rows, colwidths, colaligns, is_multiline)

        return r

    def add_row(self, row):
        row = flatten_dict(row)
        if self.columns is None:
            self.columns = list(row.keys())
        row = row.values()
        if len(row) != len(self.columns):
            raise Exception('Number of columns mismatch: {} != {}'.format(len(self.columns), len(row)))

        self.rows.append(row)
        t = tabulate.tabulate(self.rows, headers=self.columns, tablefmt='psql')
        self.prev = t

    def print(self):
        if TERMINAL.is_a_tty:
            self.default_stdout_write('\n' + self.get() + '\n' + (TERMINAL.move_up * self.height()) + TERMINAL.move_up)

    def get(self):
        return self.prev

    def height(self):
        return len(self.prev.split('\n'))

    def to_html():
        pass

    def plot():
        pass

    def cleanup(self):
        self.default_stdout_write(TERMINAL.move_down * self.height() + '\n')
        sys.stdout.write = self.default_stdout_write
