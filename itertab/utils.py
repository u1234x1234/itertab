import re


def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield str(key) + "_" + str(subkey), subvalue
            else:
                yield str(key), value

    return dict(items())


def _words_matcher(words):
    """Construct a regexp that matches any of `words`"""
    reg_exp = "|".join("{}".format(word) for word in words)
    return re.compile(reg_exp, re.I)


class OrderMatcher:
    def __init__(self):
        asc_meanings = [
            "acc",
            "prec",
            "recall",
            "f1",
            "auc",
            "quality",
            "iou",
            "map",
            "dice",
            "jaccard",
            "score",
            "lrap",
        ]
        desc_meanings = [
            "loss",
            "entropy",
            "ce",
            "divergence",
            "error",
            "time",
            "bpc",
            "bpb",
            "bit_per",
            "bit per",
            "chi",
            "mape",
            "mse",
            "mae",
        ]
        none_meanings = ["date"]
        self._asc_pattern_matcher = _words_matcher(asc_meanings)
        self._desc_pattern_matcher = _words_matcher(desc_meanings)
        self._none_pattern_matcher = _words_matcher(none_meanings)

    def predict(self, name):
        """Predict whether the `name` matches ascending or descending orders of improvements"""
        r1 = self._asc_pattern_matcher.findall(name)
        r2 = self._desc_pattern_matcher.findall(name)
        matches = []
        for x in r1:
            matches.append((len(x), 0))
        for x in r2:
            matches.append((len(x), 1))
        matches = sorted(matches, key=lambda x: -x[0])
        if matches:
            if matches[0][1] == 0:
                return "asc"
            else:
                return "desc"

        return None
