import re


def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield str(key) + '_' + str(subkey), subvalue
            else:
                yield str(key), value

    return dict(items())


def _words_matcher(words):
    """Construct a regexp that matches any of `words`
    """
    reg_exp = '|'.join('(?={})'.format(word) for word in words)
    return re.compile(reg_exp, re.I)


class OrderMatcher:
    def __init__(self):
        asc_meanings = ['acc', 'prec', 'recall', 'f1', 'auc']
        desc_meanings = ['loss', 'entropy', 'ce', 'divergence']
        self._asc_pattern_matcher = _words_matcher(asc_meanings)
        self._desc_pattern_matcher = _words_matcher(desc_meanings)

    def predict(self, name):
        """Predict whether the `name` matches ascending or descending orders of improvements
        """
        if self._asc_pattern_matcher.findall(name):
            return 'asc'
        if self._desc_pattern_matcher.findall(name):
            return 'desc'
        return None
