from datetime import datetime

import numpy as np
import pandas as pd
from blessings import Terminal
from tabulate import tabulate

from .pretty_array import PrettyArray, AvgArray
from .utils import OrderMatcher, flatten_dict

AVG_SUFFIX = "__avg"


class PrettyTable:
    """A pretty formatted table with colorized columns and cell highlighting."""

    def __init__(
        self,
        tablefmt="psql",
        auto_datetime_fmt="%b/%d/%Y %H:%M:%S",
        headers=None,
        highlight_best=True,
        show_diff=False,
        avg_columns=(),
    ):  # TODO asc,desc option
        self.tablefmt = tablefmt
        self.auto_datetime_fmt = auto_datetime_fmt
        self.show_diff = show_diff

        self._order_matcher = OrderMatcher()

        self._headers = headers if headers is not None else []
        self._columns = dict()
        self._terminal = Terminal()
        self._row_idx = 0
        self._avg_columns = (
            avg_columns if isinstance(avg_columns, tuple) else (avg_columns,)
        )

    @staticmethod
    def process_name(key):
        return key.split("___")[0]

    def add_row(self, row):
        row = flatten_dict(row)

        if self.auto_datetime_fmt:
            row = {
                "datetime": str(datetime.now().strftime(self.auto_datetime_fmt)),
                **row,
            }

        for key in row.keys():
            if len(key.split("___")) == 2:
                column_name, fmt = key.split("___")
            else:
                column_name, fmt = key, "{:.4f}"

            if key not in self._headers:
                predicted_direction = self._order_matcher.predict(column_name)

                arr = PrettyArray(
                    direction=predicted_direction,
                    show_percentage=self.show_diff,
                    fmt=fmt,
                )

                # Fill array with None to ensure that all arrays are the same length
                [arr.add(None) for _ in range(self._row_idx)]
                self._columns[column_name] = arr
                self._headers.append(key)

        for avg_col in self._avg_columns:
            if avg_col in row:
                avg_col_name = f"{avg_col}{AVG_SUFFIX}"
                if avg_col_name not in self._headers:
                    predicted_direction = self._order_matcher.predict(column_name)
                    arr = AvgArray(
                        direction=predicted_direction,
                        show_percentage=False,
                        fmt="{:.4f}",
                    )
                    [arr.add(None) for _ in range(self._row_idx)]
                    self._columns[avg_col_name] = arr
                    self._headers.append(avg_col_name)

        for column_name in self._headers:
            if column_name.endswith(AVG_SUFFIX):
                val = row[column_name[: -len(AVG_SUFFIX)]]
                self._columns[column_name].add(val)
            else:
                self._columns[self.process_name(column_name)].add(
                    row.get(column_name, None)
                )

        self._row_idx += 1

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def get_string_representation(self):
        headers = [self.process_name(x) for x in self._headers]
        rows = np.array([self._columns[key].get_colorized() for key in headers]).T
        table_str = tabulate(rows, headers=headers, tablefmt=self.tablefmt)
        return table_str

    def to_csv(self, path):
        rows = np.array([self._columns[key].get_raw_array() for key in self._headers]).T
        data_frame = pd.DataFrame(rows, columns=self._headers)
        data_frame.to_csv(path, index=False)

    def to_txt(self, path):
        headers = [self.process_name(x) for x in self._headers]
        rows = np.array([self._columns[key].get_raw_array() for key in headers]).T
        table_str = tabulate(rows, headers=headers, tablefmt=self.tablefmt)
        with open(path, "w") as out_file:
            print(table_str, file=out_file)

    def clear_screen_and_print(self):
        print(self._terminal.clear, flush=True)
        print(self)

    def __str__(self):
        return self.get_string_representation()
