import numpy as np
import pytest

from itertab.orderable_array import OrderableArray


@pytest.mark.parametrize('input_array,direction,mask', [
    ([1, 3, 2], -1, [0, -1, 1]),
    ([1, 3, 2], 1, [0, 1, -1]),
    ([1, 3, 2], 0, [0, 0, 0]),
])
def test_array(input_array, direction, mask):
    arr = OrderableArray(direction)
    [arr.add(x) for x in input_array]
    assert arr._raw_values == [str(x) for x in input_array]
    assert arr._mask == mask


def test_array_initialization():
    arr = OrderableArray(direction=1, len=3)
    assert arr._mask == [0, 0, 0]


def test_empty_array():
    arr = OrderableArray(direction=1)
    assert arr.get_colorized() == []


def test_array_min_max():
    arr = OrderableArray()
    random_values = np.random.uniform(size=100)
    [arr.add(x) for x in random_values]

    assert arr._max_idx == np.argmax(random_values)
    assert arr._max_val == np.max(random_values)

    assert arr._min_idx == np.argmin(random_values)
    assert arr._min_val == np.min(random_values)
