from typing import List, Union
import atexit
import sys

import numpy as np
from colorama import Back, Fore, Style


def float_to_string(value, n_digits_after_decimal=2):
    return (f'%.{n_digits_after_decimal}f' % value)


def is_int(value):
    """Check whether the `value` is integer.

    Args:
        value: arbitrary type value
    """
    try:
        if int(f'{value}') == int(value):
            return True
    except ValueError as e:
        pass

    return False


class PrettyArray:
    def __init__(self, array: List = [], direction: Union[str, None] = 'asc',
                 hightlight_min=True, hightlight_max=True, hightlight_nan=True,
                 show_percentage=True):

        if direction not in ['asc', 'desc', None]:
            raise ValueError('Direction should be in ["asc", "desc", None]')
        self.direction = 1 if direction == 'asc' else -1
        if direction is None:
            self.direction = 0

        self.show_percentage = show_percentage
        self.hightlight_min = hightlight_min
        self.hightlight_max = hightlight_max
        self.hightlight_nan = hightlight_nan

        self._raw_values = []
        self._order_relations = []
        self._diffs = []

        self._min_idx = None
        self._min_val = np.inf

        self._max_idx = None
        self._max_val = -np.inf

        for item in array:
            self.add(item)

        atexit.register(self._cleanup) # Reset styling at exit

    def add(self, value):
        diff = None

        try:
            float_value = float(value)
            prev_value = float(self._raw_values[-1])

            order = (float_value > prev_value) * 2 - 1  # map to {-1, 1}

            if float_value < self._min_val:
                self._min_val = float_value
                self._min_idx = len(self._raw_values)
            if float_value > self._max_val:
                self._max_val = float_value
                self._max_idx = len(self._raw_values)

            if self.show_percentage:
                diff = float_value / prev_value
                diff = diff - 1 if order == 1 else (1 - diff)
                diff = 100. * abs(diff)
                sign = ''
                if order == 1:
                    sign = '+'
                else:
                    sign = '-'
                diff = '{}{}%'.format(sign, float_to_string(diff))

            order *= self.direction

        except:
            order = 0

        self._raw_values.append(value)
        self._order_relations.append(order)
        self._diffs.append(diff)

    def get_colorized(self):
        colorized_array = []
        modifiers_map = {
            1: Fore.GREEN,
            -1: Fore.RED,
        }
        background_modifiers_map = {
            1: Back.LIGHTGREEN_EX,
            -1: Back.LIGHTRED_EX,
        }
        colorized_array = []
        for idx, (val, order_relation, ratio) in \
                enumerate(zip(self._raw_values, self._order_relations, self._diffs)):

            str_val = f'{val}'
            try:
                if not is_int(val):
                    str_val = float_to_string(float(val), 4)
            except Exception as e:
                pass
            val = str_val

            if order_relation in modifiers_map:

                if self.show_percentage and ratio is not None:
                    val = '{} ({})'.format(val, ratio)

                if self.hightlight_max and idx == self._max_idx:
                    val = background_modifiers_map[order_relation] + val + Style.RESET_ALL
                elif self.hightlight_min and idx == self._min_idx:
                    val = background_modifiers_map[order_relation] + val + Style.RESET_ALL
                else:
                    val = modifiers_map[order_relation] + val + Style.RESET_ALL

            colorized_array.append(val)

        return colorized_array

    def get_raw_array(self):
        return self._raw_values

    def _cleanup(self):
        sys.stdout.write(Style.RESET_ALL)

    def __str__(self):
        return ', '.join(self.get_colorized())
