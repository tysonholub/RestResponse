import sys
import string
import base64
import cloudpickle as pickle
from json.encoder import (
    _make_iterencode, JSONEncoder, encode_basestring_ascii, INFINITY, encode_basestring
)

PYTHON3 = sys.version_info[0] > 2


def decode_callable(value):
    if PYTHON3:
        return pickle.loads(base64.b64decode(value.replace('__callable__: b', '')))
    else:
        return pickle.loads(base64.b64decode(value.replace('__callable__: ', '')))


def decode_binary(value):
    if PYTHON3:
        return base64.b64decode(value.replace('__binary__: b', ''))
    else:
        return base64.b64decode(value.replace('__binary__: ', ''))


def encode_callable(obj):
    return '__callable__: %s' % base64.b64encode(pickle.dumps(obj))


def encode_binary(obj):
    return '__binary__: %s' % base64.b64encode(obj)


def istext(s, text_characters="".join(map(chr, range(32, 127))) + "\n\r\t\b", threshold=0.30):
    """
    Helper to attempt support of serializing binary text by base64 encoding `s` if this returns False

    Credit: https://www.oreilly.com/library/view/python-cookbook-2nd/0596007973/ch01s12.html
    """
    if PYTHON3:
        if isinstance(s, bytes):
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
