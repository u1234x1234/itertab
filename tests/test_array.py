import numpy as np
import pytest

from itertab import PrettyArray


@pytest.mark.parametrize('input_array,direction,mask', [
    ([1, 3, 2], 'desc', [0, -1, 1]),
    ([1, 3, 2, 4], 'asc', [0, 1, -1, 1]),
    ([1, 3, 2], None, [0, 0, 0]),
])
def test_array(input_array, direction, mask):
    arr = PrettyArray(direction=direction)
    [arr.add(x) for x in input_array]
    assert arr._raw_values == [x for x in input_array]
    assert arr._order_relations == mask
    arr.get_colorized()

def test_array_initialization():
    arr = PrettyArray([0, 0, 0], direction='asc')
    assert arr._order_relations == [0, 0, 0]


def test_empty_array():
    arr = PrettyArray(direction='asc')
    assert arr.get_colorized() == []


def test_array_min_max():
    arr = PrettyArray()
    random_values = np.random.uniform(size=100)
    [arr.add(x) for x in random_values]

    assert arr._max_idx == np.argmax(random_values)
    assert arr._max_val == np.max(random_values)

    assert arr._min_idx == np.argmin(random_values)
    assert arr._min_val == np.min(random_values)


def test_str():
    arr = PrettyArray([5, 2, 4, 5], show_percentage=False, direction=None)
    str_repr = str(arr)
    assert str_repr == '5, 2, 4, 5'


def test_diff():
    assert PrettyArray([1, 4])._diffs == [None, '+300.00%']
    assert PrettyArray([0.3, 0.03])._diffs == [None, '-90.00%']
    assert PrettyArray([1, -3])._diffs == [None, '-400.00%']
    assert PrettyArray([-0.3, -0.03])._diffs == [None, '+90.00%']
    assert PrettyArray([-0.3, 0.03])._diffs == [None, '+110.00%']
    assert PrettyArray([0, 0])._diffs == [None, None]
    assert PrettyArray([0.8, 0.2], direction='desc')._diffs == [None, '-75.00%']


def test_incor():
    with pytest.raises(ValueError):
        PrettyArray(direction='asd')


def test_np():
    arr = PrettyArray([np.array([1]), np.array([2])])
    assert arr._diffs == [None, '+100.00%']


def test_tuple_array_with_colorization():
    arr = PrettyArray([(1, 1), (2, 5), (3, 5), (1, 5)], show_percentage=False, fmt='{:.2f}±{:.3f}')

    assert str(arr).encode('utf-8') == b'\x1b[101m1.00\xc2\xb11.000\x1b[0m, \x1b[32m2.00\xc2\xb15.000\x1b[0m, \x1b[102m3.00\xc2\xb15.000\x1b[0m, \x1b[31m1.00\xc2\xb15.000\x1b[0m'


def test_tuple_array():
    arr = PrettyArray([(1, 1), (2, 5), (3, 5), (1, 5)], show_percentage=False, fmt='{:.2f}±{:.2f}', enable_colors=False)

    assert str(arr) == '1.00±1.00, 2.00±5.00, 3.00±5.00, 1.00±5.00'
