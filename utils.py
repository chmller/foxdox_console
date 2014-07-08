import uuid


EMPTY_UUID = uuid.UUID('{00000000-0000-0000-0000-000000000000}')


def get_safe_value_from_dict(d, k, default=None):
    if d and isinstance(d, dict):
        if k in d:
            value = d[k]
            if value is None:
                return default
            else:
                return value
        else:
            return default
    else:
        return default