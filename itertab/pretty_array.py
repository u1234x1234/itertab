import atexit
import sys
from collections import Counter
from typing import List, Union
import numpy as np
from colorama import Back, Fore, Style


def float_to_string(value, n_digits_after_decimal=2):
    return f"%.{n_digits_after_decimal}f" % value


def is_int(value):
    """Check whether the `value` is integer.

    Args:
        value: arbitrary type value
    """
    try:
        if int(f"{value}") == int(value):
            return True
    except ValueError as e:
        pass

    return False


class PrettyArray:
    def __init__(
        self,
        array: List = [],
        direction: Union[str, None] = "asc",
        fmt="{:.4f}",
        enable_colors=True,
        hightlight_min=True,
        hightlight_max=True,
        hightlight_nan=True,
        show_percentage=True,
    ):

        if direction not in ["asc", "desc", None]:
            raise ValueError('Direction should be in ["asc", "desc", None]')
        self.direction = 1 if direction == "asc" else -1
        if direction is None:
            self.direction = 0

        self._fmt = fmt
        self._enable_colors = enable_colors
        self.show_percentage = show_percentage
        self.hightlight_min = hightlight_min
        self.hightlight_max = hightlight_max
        self.hightlight_nan = hightlight_nan

        self._raw_values = []
        self._order_relations = []
        self._diffs = []

        self._min_idx = None  # non-unique min values
        self._min_val = None

        self._max_idx = None
        self._max_val = None
        self._conversion_errors = False
        self._type_counter = Counter()

        for item in array:
            self.add(item)

        atexit.register(self._cleanup)  # Reset styling at exit

    def add(self, value):
        diff = None
        order = 0

        try:
            self._type_counter[type(value)] += 1

            if self._min_val is None or value < self._min_val:
                self._min_val = value
                self._min_idx = len(self._raw_values)
            if self._max_val is None or value > self._max_val:
                self._max_val = value
                self._max_idx = len(self._raw_values)

            prev_value = self._raw_values[-1]
            greater_than_prev = value > prev_value
            if value == prev_value:
                order = 0
            else:
                order = greater_than_prev * 2 - 1

            if self.show_percentage:
                diff = float(value) / float(prev_value)
                diff = diff - 1 if greater_than_prev else (1 - diff)
                diff = 100.0 * abs(diff)
                sign = ""
                if greater_than_prev:
                    sign = "+"
                else:
                    sign = "-"
                diff = "{}{}%".format(sign, float_to_string(diff))

            order *= self.direction

        except Exception as e:
            self._conversion_errors = True

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
        if self._type_counter.get(str, 0) != 0:
            self._enable_colors = False

        for idx, (val, order_relation, ratio) in enumerate(
            zip(self._raw_values, self._order_relations, self._diffs)
        ):

            if val is None:
                val = ""
            else:
                try:
                    val = self._fmt.format(*val)
                except Exception as e:
                    val = str(val)

            if self.show_percentage and ratio is not None:
                val = "{} ({})".format(val, ratio)

            # Colorization
            if self._enable_colors:
                is_back_applied = False

                if self.direction:
                    if self.hightlight_max and idx == self._max_idx:
                        val = (
                            background_modifiers_map[self.direction]
                            + val
                            + Style.RESET_ALL
                        )
                        is_back_applied = True
                    elif self.hightlight_min and idx == self._min_idx:
                        val = (
                            background_modifiers_map[self.direction * -1]
                            + val
                            + Style.RESET_ALL
                        )
                        is_back_applied = True

                if (
                    order_relation
                    and order_relation in modifiers_map
                    and not is_back_applied
                ):
                    val = modifiers_map[order_relation] + val + Style.RESET_ALL

            colorized_array.append(val)

        return colorized_array

    def get_raw_array(self):
        return self._raw_values

    def _cleanup(self):
        sys.stdout.write(Style.RESET_ALL)

    def __str__(self):
        return ", ".join(self.get_colorized())


def _get_avg(arr, alg):
    if alg == "ma_5":
        return np.mean(arr[-5:])
    else:
        raise NotImplementedError()


class AvgArray(PrettyArray):
    "PrettyArray + averaging (moving average, exponential)"

    def __init__(self, alg="ma_5", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = []
        self._alg = alg

    def add(self, value):
        self._data.append(value)
        value = _get_avg(self._data, self._alg)
        super().add(value)
