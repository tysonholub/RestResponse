import sys
import string
import base64
from decimal import Decimal
from datetime import datetime, date
import cloudpickle as pickle
from json.encoder import (
    _make_iterencode, JSONEncoder, encode_basestring_ascii, INFINITY, encode_basestring
)

PYTHON3 = sys.version_info[0] > 2
PYTHON34 = PYTHON3 and sys.version_info[1] >= 4


def _decode_callable(value):
    return pickle.loads(base64.b64decode(value.replace('__callable__: ', '')))


def _decode_binary(value):
    return base64.b64decode(value.replace('__binary__: ', ''))


def _encode_callable(obj):
    if PYTHON3:
        return '__callable__: %s' % base64.b64encode(pickle.dumps(obj)).decode('utf-8')
    else:
        return '__callable__: %s' % base64.b64encode(pickle.dumps(obj))


def _encode_binary(obj):
    if PYTHON3:
        return '__binary__: %s' % base64.b64encode(obj).decode('utf-8')
    else:
        return '__binary__: %s' % base64.b64encode(obj)


def istext(s, text_characters="".join(map(chr, range(32, 127))) + "\n\r\t\b", threshold=0.30):
    """
    Helper to attempt support of serializing binary text by base64 encoding `s` if this returns False

    Credit: https://www.oreilly.com/library/view/python-cookbook-2nd/0596007973/ch01s12.html
    """
    if PYTHON3:
        if isinstance(s, bytes):
            try:
                s = s.decode('utf-8')
            except UnicodeDecodeError:
                return False

    if '\0' in s:
        return False
    if not s:
        return True

    if PYTHON3:
        t = s.translate(str.maketrans("", "", text_characters))
    else:
        t = s.translate(string.maketrans("", ""), text_characters)

    # s is 'text' if less than 30% of its characters are non-text ones:
    return len(t)/len(s) <= threshold


def encode_item(item, encode_binary=True, encode_callable=True, **kwargs):
    if isinstance(item, Decimal):
        return float(item)
    elif isinstance(item, datetime) or isinstance(item, date):
        return item.isoformat()
    elif encode_callable and callable(item):
        return _encode_callable(item)
    elif (
        encode_binary and
        not PYTHON3 and isinstance(item, str) and not istext(item)
        or PYTHON3 and isinstance(item, bytes) and not istext(item)
    ):
        return _encode_binary(item)
    elif (
        not PYTHON3 and isinstance(item, unicode)
        or PYTHON3 and isinstance(item, str)
    ):
        return item.encode('utf-8')
    elif PYTHON3 and isinstance(item, bytes) and istext(item):
        return item.decode('utf-8')
    return item


def decode_item(item, decode_binary=True, decode_callable=True, **kwargs):
    if isinstance(item, Decimal):
        return float(item)
    elif decode_callable and isinstance(item, str) and item.startswith('__callable__: '):
        return _decode_callable(item)
    elif decode_callable and PYTHON3 and isinstance(item, bytes) and item.startswith(b'__callable__: '):
        return _decode_callable(item.decode('utf-8'))
    elif decode_callable and not PYTHON3 and isinstance(item, unicode) and item.startswith('__callable__: '):
        return _decode_callable(item)
    elif decode_binary and isinstance(item, str) and item.startswith('__binary__: '):
        return _decode_binary(item)
    elif decode_binary and PYTHON3 and isinstance(item, bytes) and item.startswith(b'__binary__: '):
        return _decode_binary(item.decode('utf-8'))
    elif decode_binary and not PYTHON3 and isinstance(item, unicode) and item.startswith('__binary__: '):
        return _decode_binary(item)
    try:
        if PYTHON3 and isinstance(item, bytes):
            return item.decode('utf-8')
        elif not PYTHON3 and isinstance(item, str):
            return item.decode('utf-8')
    except UnicodeDecodeError:
        pass
    return item


class CustomObjectEncoder(JSONEncoder):
    """
    Credit: https://stackoverflow.com/questions/16405969/how-to-change-json-encoding-behaviour-for-serializable-python-object/16406798#answer-17684652  # NOQA
    """
    def iterencode(self, o, _one_shot=False):
        """
        Most of the original method has been left untouched.

        _one_shot is forced to False to prevent c_make_encoder from
        being used. c_make_encoder is a funcion defined in C, so it's easier
        to avoid using it than overriding/redefining it.

        The keyword argument isinstance for _make_iterencode has been set
        to self.isinstance. This allows for a custom isinstance function
        to be defined, which can be used to defer the serialization of custom
        objects to the default method.
        """
        # Force the use of _make_iterencode instead of c_make_encoder
        _one_shot = False

        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        if not PYTHON3:
            if self.encoding != 'utf-8':
                def _encoder(o, _orig_encoder=_encoder, _encoding=self.encoding):
                    if isinstance(o, str):
                        o = o.decode(_encoding)
                    return _orig_encoder(o)

        def floatstr(o, allow_nan=self.allow_nan,
                     _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text

        _iterencode = _make_iterencode(
            markers, self.default, _encoder, self.indent, floatstr,
            self.key_separator, self.item_separator, self.sort_keys,
            self.skipkeys, _one_shot, isinstance=self.isinstance)

        return _iterencode(o, 0)
