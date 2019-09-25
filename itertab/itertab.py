# -*- coding: utf-8 -*-
import atexit
import sys

from blessings import Terminal

from .pretty_table import PrettyTable

TERMINAL = Terminal()
CLEAR = '\033[K'


class Table(PrettyTable):
    def __init__(self, *args, **kwargs):
        super().__init__(self, args, kwargs)

        self._table = PrettyTable()

        atexit.register(self.cleanup)
        self.default_stdout_write = sys.stdout.write
        sys.stdout.write = self.patched_write

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
        self._table.add_row(row)

    def get(self):
        self.clear()
        return self._table.get_string_representation()

    def height(self):
        return len(self._table.get_string_representation().split('\n'))

    def cleanup(self):
        self.default_stdout_write(TERMINAL.move_down * self.height() + ('\n' + CLEAR))
        sys.stdout.write = self.default_stdout_write
