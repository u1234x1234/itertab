# -*- coding: utf-8 -*-
import atexit
import os
import sys
from datetime import datetime

import tabulate
from blessings import Terminal

from .pretty_table import PrettyTable

TERMINAL = Terminal()
CLEAR = '\033[K'


class Table:
    def __init__(self, auto_datetime_fmt=None):
        self._table = PrettyTable()

        self.auto_datetime_fmt = auto_datetime_fmt
        atexit.register(self.cleanup)
        self.default_stdout_write = sys.stdout.write
        # sys.stdout.write = self.patched_write

    def update(self, row):
        self._add_print(row)

    def patched_write(self, q):
        if TERMINAL.is_a_tty:
            self.default_stdout_write(q + CLEAR)
            tt = self.get()
            self.default_stdout_write('\n' + tt + '\n' + (TERMINAL.move_up * self.height()) + TERMINAL.move_up)
        else:
            self.default_stdout_write(q)

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
        return self._table.get()

    def height(self):
        return len(self._table.get().split('\n'))

    def to_csv(self, filename):
        self._table.to_csv(filename)

    def to_html():
        pass

    def plot():
        pass

    def cleanup(self):
        self.default_stdout_write(TERMINAL.move_down * self.height() + ('\n' + CLEAR))
        sys.stdout.write = self.default_stdout_write
