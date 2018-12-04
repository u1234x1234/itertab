import pytest

from itertab.pretty_table import PrettyTable
from itertab.pretty_table import OrderableArray

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
