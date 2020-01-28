import base64
from decimal import Decimal
from datetime import datetime, date
import cloudpickle as pickle


def _decode_callable(value):
    return pickle.loads(base64.b64decode(value.replace('__callable__: ', '')))


def _decode_binary(value):
    return base64.b64decode(value.replace('__binary__: ', ''))


def _encode_callable(obj):
    return '__callable__: %s' % base64.b64encode(pickle.dumps(obj)).decode('utf-8')


def _encode_binary(obj):
    return '__binary__: %s' % base64.b64encode(obj).decode('utf-8')


def istext(s, text_characters="".join(map(chr, range(32, 127))) + "\n\r\t\b", threshold=0.30):
    """
    Helper to attempt support of serializing binary text by base64 encoding `s` if this returns False

    Credit: https://www.oreilly.com/library/view/python-cookbook-2nd/0596007973/ch01s12.html
    """
    if isinstance(s, bytes):
        try:
            s = s.decode('utf-8')
        except UnicodeDecodeError:
            return False

    if '\0' in s:
        return False
    if not s:
        return True

    t = s.translate(str.maketrans("", "", text_characters))

    # s is 'text' if less than 30% of its characters are non-text ones:
    return len(t) / len(s) <= threshold


def encode_item(item, encode_binary=True, encode_callable=True, **kwargs):
    if isinstance(item, Decimal):
        return float(item)
    elif isinstance(item, datetime):
        if 'encode_datetime' in kwargs and callable(kwargs.get('encode_datetime')):
            return kwargs.get('encode_datetime')(item)
        else:
            return item.isoformat()
    elif isinstance(item, date):
        if 'encode_date' in kwargs and callable(kwargs.get('encode_date')):
            return kwargs.get('encode_date')(item)
        else:
            return item.isoformat()
    if encode_callable and callable(item):
        return _encode_callable(item)
    elif (
        encode_binary and isinstance(item, bytes) and not istext(item)
    ):
        return _encode_binary(item)
    elif isinstance(item, bytes) and istext(item):
        return item.decode('utf-8')
    return item


def decode_item(item, decode_binary=True, decode_callable=True, **kwargs):
    if isinstance(item, Decimal):
        return float(item)
    elif decode_callable and isinstance(item, str) and item.startswith('__callable__: '):
        return _decode_callable(item)
    elif decode_callable and isinstance(item, bytes) and item.startswith(b'__callable__: '):
        return _decode_callable(item.decode('utf-8'))
    elif decode_binary and isinstance(item, str) and item.startswith('__binary__: '):
        item = _decode_binary(item)
    elif decode_binary and isinstance(item, bytes) and item.startswith(b'__binary__: '):
        item = _decode_binary(item.decode('utf-8'))
    try:
        if isinstance(item, bytes):
            item = item.decode('utf-8')
    except UnicodeDecodeError:
        pass
    return item
