# -*- coding: utf-8 -*-
import atexit
import sys

from blessings import Terminal

from .pretty_table import PrettyTable

CLEAR = '\033[K'


class Table(PrettyTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        atexit.register(self.return_cursor)
        self.default_stdout_write = sys.stdout.write
        sys.stdout.write = self.patched_write

    def patched_write(self, q):
        if self._terminal.is_a_tty:
            self.default_stdout_write(q + CLEAR)
            tt = self.get()
            self.default_stdout_write('\n' + tt + '\n' + (self._terminal.move_up * self.height()) + self._terminal.move_up)
        else:
            self.default_stdout_write(q)

    def _print(self):
        if self._terminal.is_a_tty:
            self.default_stdout_write('\n' + self.get() + '\n' + (self._terminal.move_up * self.height()) + self._terminal.move_up)

    def _add_print(self, row):
        self.add_row(row)
        self._print()

    def clear(self):
        self.default_stdout_write(('\n' + CLEAR) * self.height() + self._terminal.move_up * self.height())

    def get(self):
        self.clear()
        return self.get_string_representation()

    def height(self):
        return len(self.get_string_representation().split('\n'))

    def return_cursor(self):
        self.default_stdout_write(self._terminal.move_down * self.height() + ('\n' + CLEAR))
        sys.stdout.write = self.default_stdout_write
