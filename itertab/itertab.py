# -*- coding: utf-8 -*-
import atexit
import os
import sys

import numpy as np
import tabulate
from blessings import Terminal
from colorama import Back, Fore, Style
from tabulate import _format_table as default_format


TERMINAL = Terminal()


def _format_table(fmt, headers, rows, colwidths, colaligns, is_multiline):
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
            if float_column[i] > float_column[i - 1]:  # TODO ==
                m_row.append(Fore.GREEN + col[i] + Style.RESET_ALL)
            else:
                m_row.append(Fore.RED + col[i] + Style.RESET_ALL)
        modified_rows.append(m_row)
    rows = list(map(list, zip(*modified_rows)))
    r = default_format(fmt, headers, rows, colwidths, colaligns, is_multiline)

    return r


class Table:
    def __init__(self, columns):
        self.columns = columns
        self.rows = []
        self.prev = ''
        atexit.register(self.cleanup)
        tabulate._format_table = _format_table
        self.default_stdout_write = sys.stdout.write
        sys.stdout.write = self.patched_write

    def patched_write(self, q):
        if TERMINAL.is_a_tty:
            self.default_stdout_write(q + '\033[K')
            tt = self.get()
            self.default_stdout_write('\n' + tt + '\n' + (TERMINAL.move_up * self.height()) + TERMINAL.move_up)
        else:
            self.default_stdout_write(q)

    def add_row(self, row):
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
