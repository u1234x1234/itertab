import numpy as np
import pytest

from itertab import PrettyTable
from itertab.itertab import Table


gt = """
+------+------+
|   m1 |   m2 |
|------+------|
|    1 |    1 |
|    2 |    2 |
+------+------+
""".strip()


def test_pretty_table():
    t1 = PrettyTable(auto_datetime_fmt=None)
    t1.add_rows([{'m1': 1, 'm2': 1}, {'m1': 2, 'm2': 2}])
    r = str(t1)
    assert gt == r


def test_table():
    t2 = Table(auto_datetime_fmt=None)
    t2.add_rows([{'m1': 1, 'm2': 1}, {'m1': 2, 'm2': 2}])
    r = str(t2)
    assert gt == r
    assert t2.height() == len(gt.split('\n'))


def test_to_csv():
    t = PrettyTable(auto_datetime_fmt=None)
    t.add_rows([{'m1': 1, 'm2': 1}, {'m1': 2, 'm2': 2}])
    path = '/tmp/1.csv'
    t.to_csv(path)
    with open(path, 'r') as in_file:
        r = in_file.read()

    assert 'm1,m2\n1,1\n2,2' == r.strip()


def test_empty_cells():

    gt = """+----------+-----------+
| asdasd   | new_row   |
|----------+-----------|
| 1        |           |
| 2        | 123       |
| 3        | 3535      |
|          | 3535      |
+----------+-----------+"""


    table = PrettyTable(auto_datetime_fmt=None)

    rows = [
        {'asdasd': 1},
        {'asdasd': 2, 'new_row': 123},
        {'asdasd': 3, 'new_row': 3535},
        {'new_row': 3535},
    ]

    table.add_rows(rows)
    assert str(table) == gt
