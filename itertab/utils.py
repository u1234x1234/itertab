def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield str(key) + '_' + str(subkey), subvalue
            else:
                yield str(key), value

    return dict(items()) 
