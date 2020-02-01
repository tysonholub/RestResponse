import json
import warnings
from datetime import datetime, date

import autoviv
from autoviv import NoneProp
import simplejson
from dateutil import parser as dateutil_parser
from sqlalchemy.ext.mutable import Mutable

from RestResponse import utils


def _encode_hook(opts):
    def _default(o):
        if isinstance(o, ApiModel):
            return o._data
        return utils.encode_item(o, **opts)
    return _default


def _decode_hook(obj):
    for k, v in obj.items():
        obj[k] = utils.decode_item(v)
    return obj


class RestEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(RestEncoder, self).__init__(*args, **kwargs)
        setattr(self, 'default', _encode_hook({}))


class RestEncoderSimple(simplejson.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(RestEncoderSimple, self).__init__(*args, **kwargs)
        setattr(self, 'default', _encode_hook({}))

    def iterencode(self, o, *args, **kwargs):
        try:
            return super(RestEncoderSimple, self).iterencode(o, *args, **kwargs)
        except Exception:
            # this could use a better solution
            return super(RestEncoderSimple, self).iterencode(json.loads(str(o)), *args, **kwargs)


json._default_encoder = RestEncoder()
simplejson._default_encoder = RestEncoderSimple()


class RestResponseObj(Mutable, object):
    __opts__ = {
        'encode_binary': True,
        'encode_callable': True,
        'decode_binary': True,
        'decode_callable': True
    }

    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, dict) and not isinstance(value, RestObject):
            return RestObject(value)
        elif isinstance(value, list) and not isinstance(value, RestList):
            return RestList(value)
        else:
            return value

    def changed(self):
        super(RestResponseObj, self).changed()

    def __call__(self):
        return self


class RestList(RestResponseObj, autoviv.List):
    def __init__(self, iterable=()):
        for x in iter(iterable):
            self.append(x)

    def __repr__(self):
        return autoviv.pprint(self, indent=None, cls=RestEncoder)

    def pretty_print(self, indent=4):
        return autoviv.pprint(self, indent=indent, cls=RestEncoder)

    def __setitem__(self, index, item):
        if isinstance(item, NoneProp):
            return

        item = RestResponse.parse(item)

        super(RestList, self).__setitem__(index, item)
        self.changed()

    def append(self, item):
        self.insert(len(self), item)
        self.changed()

    def extend(self, items):
        for item in items:
            self.append(item)

    def insert(self, index, item):
        if isinstance(item, NoneProp):
            return

        item = RestResponse.parse(item)

        super(RestList, self).insert(index, item)
        self.changed()

    def pop(self, index=None):
        if index:
            item = super(RestList, self).pop(index)
        else:
            item = super(RestList, self).pop()

        self.changed()
        return item

    def remove(self, item):
        super(RestList, self).remove(item)
        self.changed()


class RestObject(RestResponseObj, autoviv.Dict):
    def __init__(self, *args, **kwargs):
        super(RestObject, self).__init__()
        self.update(*args, **kwargs)

    def __repr__(self):
        return self.pretty_print(indent=None)

    def __str__(self):
        return self.pretty_print(indent=None)

    def pretty_print(self, indent=4):
        return autoviv.pprint(self, indent=indent, cls=RestEncoder)

    def __delattr__(self, name):
        if name in self:
            del self[name]
            self.changed()

    def clear(self):
        super(RestObject, self).clear()
        self.changed()

    def pop(self, name, default=None):
        if name in self:
            value = super(RestObject, self).pop(name, default)
            self.changed()
        else:
            value = default
        return value

    def popitem(self):
        value = super(RestObject, self).popitem()
        self.changed()
        return value

    def __missing__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, key):
        if key in self:
            value = self[key]
            return value
        elif key == '__clause_element__':
            # SQLAlchemy will try to call this prop, raise AttributeError to avoid
            raise AttributeError(key)
        else:
            return super(RestObject, self).__getattr__(key)

    def __setattr__(self, key, value):
        if isinstance(value, NoneProp):
            return
        if key != '__none_props__':
            value = RestResponse.parse(value)

        super(RestObject, self).__setattr__(key, value)
        self.changed()

    def update(self, *args, **kwargs):
        result = {}
        for k, v in dict(*args, **kwargs).items():
            result[k] = RestResponse.parse(v)

        super(RestObject, self).update(**result)
        self.changed()


class RestResponse(object):
    def __new__(self, data, **kwargs):
        if isinstance(data, str):
            return RestResponse.loads(data)
        else:
            return RestResponse.parse(data)

    @staticmethod
    def parse(data):
        if isinstance(data, RestResponseObj) or isinstance(data, NoneProp):
            return data
        elif isinstance(data, dict):
            return RestObject(data)
        elif isinstance(data, list):
            return RestList(data)
        else:
            return data

    @staticmethod
    def loads(data, **kwargs):
        try:
            data = json.loads(data, object_hook=_decode_hook, **kwargs)
        except Exception:
            raise ValueError('RestResponse data must be JSON deserializable')

        return RestResponse.parse(data)


class ApiModel(object):
    __opts__ = {
        'encode_binary': False,
        'encode_callable': False,
        'decode_binary': False,
        'decode_callable': False,
        'encode_datetime': lambda x: datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'),
        'encode_date': lambda x: datetime.strftime(x, '%Y-%m-%d'),
        '_overrides': [],
    }

    def __bool__(self):
        return bool(self._data)

    def __nonzero__(self):
        return bool(self._data)

    def __eq__(self, other):
        if not isinstance(other, ApiModel):
            return False
        return self._data == other._data

    @property
    def _data(self):
        return self.__data

    @_data.setter
    def _data(self, data):
        data = data or RestResponse.parse({})
        if isinstance(data, dict) or isinstance(data, list):
            data = RestResponse.parse(data)
        elif isinstance(data, str):
            try:
                data = RestResponse.loads(data or "{}")
            except ValueError as e:
                raise ValueError('{0} data must be JSON serializable'.format(self.__class__)) from e
        elif isinstance(data, ApiModel):
            data = data._data

        self.__data = RestResponse.parse({})
        for prop in dir(self):
            if (not prop.startswith('_') or prop in self.__opts__.get('_overrides', [])) and prop in data:
                setattr(self, prop, data[prop])

    @property
    def _as_json(self):
        return json.loads(json.dumps(self._data, default=_encode_hook(self.__opts__)))

    def _set_datetime(self, d, format='%Y-%m-%dT%H:%M:%SZ'):
        return self._format_datetime(d, format=format, raises_value_error=True)

    def _get_datetime(self, d, format='%Y-%m-%dT%H:%M:%SZ'):
        return self._format_datetime(d, format=format, raises_value_error=False)

    def _format_datetime(self, d, format='%Y-%m-%dT%H:%M:%SZ', raises_value_error=False):
        if not isinstance(d, datetime) or not isinstance(d, date):
            try:
                d = dateutil_parser.parse(d)
                return datetime.strptime(d.strftime(format), format)
            except ValueError:
                if raises_value_error:
                    raise
                else:
                    warnings.warn('Value must be date or datetime')
                    return None
        else:
            return d

    def _set_date(self, d, format='%Y-%m-%d'):
        return self._format_date(d, format=format, raises_value_error=True)

    def _get_date(self, d, format='%Y-%m-%d'):
        return self._format_date(d, format=format, raises_value_error=False)

    def _format_date(self, d, format='%Y-%m-%d', raises_value_error=False):
        if not isinstance(d, date):
            try:
                d = dateutil_parser.parse(d)
                return datetime.strptime(d.strftime(format), format).date()
            except ValueError:
                if raises_value_error:
                    raise
                else:
                    warnings.warn('Value must be date')
                    return None
        else:
            return d

    def _set_string(self, s):
        return self._format_string(s, raises_value_error=True)

    def _get_string(self, s):
        return self._format_string(s, raises_value_error=False)

    def _format_string(self, s, raises_value_error=False):
        if raises_value_error and not isinstance(s, str):
            raise ValueError('Value must be str')
        return '%s' % (s or '')

    def _set_float(self, f):
        return self._format_float(f, raises_value_error=True)

    def _get_float(self, f):
        return self._format_float(f, raises_value_error=False)

    def _format_float(self, f, raises_value_error=False):
        try:
            return float(f)
        except (ValueError, TypeError):
            if raises_value_error:
                raise
            else:
                warnings.warn('Value must be float')
                return None

    def _set_int(self, i):
        return self._format_int(i, raises_value_error=True)

    def _get_int(self, i):
        return self._format_int(i, raises_value_error=False)

    def _format_int(self, i, raises_value_error=False):
        try:
            return int(i)
        except (ValueError, TypeError):
            if raises_value_error:
                raise
            else:
                warnings.warn('Value must be integer')
                return None

    def _set_bool(self, b):
        return self._format_bool(b, raises_value_error=True)

    def _get_bool(self, b):
        return self._format_bool(b, raises_value_error=False)

    def _format_bool(self, b, raises_value_error=False):
        if (
            raises_value_error
            and not isinstance(b, bool)
        ):
            raise ValueError('Value must be bool')
        return b in [True, 'True', 'true', '1', 1]


class ApiCollection(RestList):
    def __init__(self, setter, iterable=(), **setter_kwargs):
        self.setter = setter
        self.setter_kwargs = setter_kwargs
        self.extend(iterable)

    @property
    def _data(self):
        return RestResponse.parse([x for x in self])

    @property
    def _as_json(self):
        return json.loads(json.dumps(self, default=_encode_hook(self.__opts__)))

    def append(self, item):
        self.insert(len(self), item)

    def insert(self, index, item):
        value = self.setter(item, **self.setter_kwargs)
        if value is not None:
            super(ApiCollection, self).insert(index, value)

    def extend(self, items):
        for item in items:
            self.append(item)

    def __setitem__(self, index, value):
        if index >= 0 and index < len(self):
            self.pop(index)
            self.insert(index, value)
        else:
            raise IndexError('list index out of range')
