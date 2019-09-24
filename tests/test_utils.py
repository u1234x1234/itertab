
from itertab.utils import OrderMatcher
from itertab.utils import flatten_dict


def test_order_matcher():
    matcher = OrderMatcher()
    assert matcher.predict('Accuracy') == 'asc'
    assert matcher.predict('Discriminator_loss') == 'desc'
    assert matcher.predict('dt') == None
    assert matcher.predict('ROC-AUC') == 'asc'


def test_flatten_dict():
    d = {
        'sub_dict': {
            'sub_key1': 1,
            'sub_key2': 2,
        },
        'key3': 3,
    }
    flattened = {
        'sub_dict_sub_key1': 1,
        'sub_dict_sub_key2': 2,
        'key3': 3,
    }
    assert flatten_dict(d) == flattened
