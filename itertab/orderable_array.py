import numpy as np
from colorama import Back, Fore, Style


class OrderableArray:
    def __init__(self, direction: int=1, len: int=0):
        if direction not in {-1, 0, 1}:
            raise ValueError('Direction not in {-1, 0, 1}')

        self.direction = direction

        self._raw_values = [None for _ in range(len)]
        self._mask = [0 for _ in range(len)]

        self._min_idx = None
        self._min_val = np.inf

        self._max_idx = None
        self._max_val = -np.inf

    def add(self, value):
        try:
            float_value = float(value)
            order = (float_value > float(self._raw_values[-1])) * 2 - 1  # map to {-1, 1}
            order *= self.direction
            if float_value < self._min_val:
                self._min_val = float_value
                self._min_idx = len(self._raw_values)
            if float_value > self._max_val:
                self._max_val = float_value
                self._max_idx = len(self._raw_values)
        except:
            order = 0

        self._raw_values.append(str(value))
        self._mask.append(order)

    def get_colorized(self, highlight_min=True, highlight_max=True):
        colorized_array = []
        modifiers_map = {
            1: Fore.GREEN,
            -1: Fore.RED,
        }
        colorized_array = []
        for val, fl in zip(self._raw_values, self._mask):
            if fl in modifiers_map:
                colorized_array.append(modifiers_map[fl] + val + Style.RESET_ALL)
            else:
                colorized_array.append(val)

        return colorized_array
