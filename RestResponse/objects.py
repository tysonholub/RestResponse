# from __future__ import division, absolute_import, print_function, unicode_literals

import json
import six
import base64
import cloudpickle as pickle
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.ext.mutable import Mutable
from RestResponse.utils import istext, CustomObjectEncoder


class RestEncoder(CustomObjectEncoder):
    def isinstance(self, obj, cls):
        if isinstance(obj, (RestResponseObj, NoneProp)):
            return False
        return isinstance(obj, cls)

    def _walk_dict(self, obj):
        result = {}
        for k, v in six.iteritems(obj):
            if isinstance(v, dict):
                result[k] = self._walk_dict(v)
            elif isinstance(v, list):
                result[k] = self._recurse_list(v)
            elif isinstance(v, Decimal):
                result[k] = float(v)
            elif isinstance(v, datetime) or isinstance(v, date):
                result[k] = v.isoformat()
            elif isinstance(v, str) and not istext(v):
                result[k] = '__binary__: %s' % base64.b64encode(v)
            elif callable(v):
                result[k] = '__callable__: %s' % base64.b64encode(pickle.dumps(v))
            else:
                if isinstance(v, NoneProp):
                    v = None
                result[k] = v

        return result

    def _recurse_list(self, obj):
        result = []
        for item in obj:
            if isinstance(item, list):
                result.append(self._recurse_list(item))
            elif isinstance(item, dict):
                result.append(self._walk_dict(item))
            elif isinstance(item, Decimal):
                result.append(float(item))
            elif isinstance(item, datetime) or isinstance(item, date):
                result.append(item.isoformat())
            elif isinstance(item, str) and not istext(item):
                result.append('__binary__: %s' % base64.b64encode(item))
            elif callable(item):
                result.append('__callable__: %s' % base64.b64encode(pickle.dumps(item)))
            else:
                if isinstance(item, NoneProp):
                    item = None
                result.append(item)

        return result

    def default(self, obj):
        if isinstance(obj, list):
            return self._recurse_list(obj)
        elif isinstance(obj, dict):
            return self._walk_dict(obj)
        elif isinstance(obj, NoneProp):
            obj = None
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, str) and not istext(obj):
            return '__binary__: %s' % base64.b64encode(obj)
        elif callable(obj):
            return '__callable__: %s' % base64.b64encode(pickle.dumps(obj))

        else:
            return None


class RestResponseObj(Mutable, object):
    __parent__ = None

    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, dict) and not isinstance(value, RestObject):
            return RestObject(value)
        elif isinstance(value, list) and not isinstance(value, RestList):
            return RestList(value)
        else:
            return value

    def changed(self):
        if self.__parent__:
            self.__parent__.changed()
        else:
            super(RestResponseObj, self).changed()

    def __call__(self):
        return json.loads(json.dumps(self, cls=RestEncoder))


class NoneProp(object):
    def __init__(self, parent, prop):
        self.__parent__ = parent
        self.__prop__ = prop

    def __eq__(self, other):
        return other is None

    def __lt__(self, other):
        return other is not None

    def __gt__(self, other):
        return False

    def __str__(self):
        return 'None'

    def __repr__(self):
        return 'None'

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False

    def __len__(self):
        return 0

    def __call__(self):
        return None

    def __setattr__(self, name, value):
        if name == '__parent__' or name == '__prop__':
            super(NoneProp, self).__setattr__(name, value)
        else:
            parent = self.__parent__
            props = [self.__prop__]
            while type(parent) != RestObject:
                props.append(parent.__prop__)
                parent = parent.__parent__

            result = {
                name: value
            }

            for p in props:
                result = {
                    p: result
                }

            parent._update_object(result)

    def __delattr__(self, name):
        pass

    def __getattr__(self, name):
        return NoneProp(self, name)


class RestList(RestResponseObj, list):
    def __init__(self, data, parent=None):
        if not isinstance(data, list):
            raise ValueError('RestList data must be list object')

        self.__parent__ = parent

        for item in data:
            self.append(item)

    @property
    def __data__(self):
        return json.loads(self.pretty_print())

    def pretty_print(self, indent=4):
        return json.dumps(self, cls=RestEncoder, indent=indent)

    def __repr__(self):
        return super(RestList, self).__repr__()

    def __getitem__(self, index):
        item = super(RestList, self).__getitem__(index)
        if str(item).startswith('__callable__: '):
            item = pickle.loads(base64.b64decode(item.replace('__callable__: ', '')))
        elif str(item).startswith('__binary__: '):
            item = base64.b64decode(item.replace('__binary__: ', ''))
        return item

    def __iter__(self):
        for item in list.__iter__(self):
            if str(item).startswith('__callable__: '):
                yield pickle.loads(base64.b64decode(item.replace('__callable__: ', '')))
            elif str(item).startswith('__binary__: '):
                yield base64.b64decode(item.replace('__binary__: ', ''))
            else:
                yield item

    def append(self, item):
        if callable(item):
            item = '__callable__: %s' % base64.b64encode(pickle.dumps(item))
        elif isinstance(item, str) and not istext(item):
            item = '__binary__: %s' % base64.b64encode(item)
        super(RestList, self).append(RestResponse.parse(item, parent=self))
        self.changed()

    def extend(self, items):
        for item in items:
            self.append(item)

    def insert(self, index, item):
        if str(item).startswith('__callable__: '):
            item = pickle.loads(item.replace('__callable__: ', ''))
        elif str(item).startswith('__binary__: '):
            item = base64.b64decode(item.replace('__binary__: ', ''))
        super(RestList, self).insert(index, RestResponse.parse(item, parent=self))
        self.changed()

    def pop(self):
        value = super(RestList, self).pop()
        self.changed()
        return value

    def remove(self, item):
        super(RestList, self).remove(item)
        self.changed()


class RestObject(RestResponseObj, dict):
    def __init__(self, data, parent=None):
        if not isinstance(data, dict):
            raise ValueError('RestObject data must be dict object')
        self.__data__ = {}
        self.__parent__ = parent
        for k, v in six.iteritems(data):
            self.__data__[k] = self._init_data(v)

    def __repr__(self):
        return json.dumps(self, cls=RestEncoder, indent=None)

    def __str__(self):
        return self.pretty_print(indent=None)

    def __contains__(self, key):
        return key in self.__data__

    def __len__(self):
        return len(self.__data__)

    def pretty_print(self, indent=4):
        return json.dumps(self, cls=RestEncoder, indent=indent)

    def __dir__(self):
        return dir(self.__data__) + self.keys()

    def __delattr__(self, name):
        if name in self.__data__:
            del self.__data__[name]
            self.changed()

    def clear(self):
        self.__data__ = {}
        self.changed()

    def pop(self, name):
        if name in self.__data__:
            value = self.__data__.pop(name)
            self.changed()
            return value
        else:
            return None

    def popitem(self, name):
        if name in self.__data__:
            value = self.__data__.pop(name)
            self.changed()
            return (name, value)
        else:
            return None

    def __iter__(self):
        for x in self.keys():
            yield x

    def __eq__(self, other):
        if type(other) == type(self):
            return self.__data__ == other.__data__
        else:
            return False

    def __bool__(self):
        return bool(self.__data__)

    def __nonzero__(self):
        return bool(self.__data__)

    def __getattr__(self, name):
        if name in self.__data__:
            return self.__data__.get(name)
        elif name == '__clause_element__':
            # SQLAlchmey TypeDecorator support
            # if we don't filter this prop, SQLAlchemy will __call__ on NoneProp
            raise AttributeError(name)
        elif name == '__parent__':
            return self.__parent__
        else:
            return NoneProp(self, name)

    def __setattr__(self, name, value):
        if name == '__data__' or name == '__parent__':
            super(RestObject, self).__setattr__(name, value)
        else:
            self._update_object({name: value})

    def keys(self):
        return self.__data__.keys()

    def get(self, key, default=None):
        return self.__data__.get(key, default)

    def has_key(self, key):
        return key in self.__data__

    def items(self):
        return self.__data__.items()

    def iteritems(self):
        return six.iteritems(self.__data__)

    def iterkeys(self):
        return self.__data__.iterkeys()

    def itervalues(self):
        return self.__data__.itervalues()

    def values(self):
        return self.__data__.values()

    def viewitems(self):
        return self.__data__.viewitems()

    def viewkeys(self):
        return self.__data__.viewkeys()

    def viewvalues(self):
        return self.__data__.viewvalues()

    def update(self, data):
        if isinstance(data, dict):
            self._update_object(data)

    def _init_data(self, v):
        if isinstance(v, dict) and not isinstance(v, RestObject):
            v = RestObject(v, parent=self)
        elif isinstance(v, list) and not isinstance(v, RestList):
            v = RestList(v, parent=self)
        elif isinstance(v, Decimal):
            v = float(v)
        elif isinstance(str(v), str) and str(v).startswith('__callable__: '):
            v = pickle.loads(base64.b64decode(str(v).replace('__callable__: ', '')))
        elif isinstance(str(v), str) and str(v).startswith('__binary__: '):
            v = base64.b64decode(str(v).replace('__binary__: ', ''))
        return v

    def _update_object(self, data):
        for k, v in six.iteritems(data):
            self.__data__[k] = self._init_data(v)
        self.changed()


class RestResponse(object):
    def __new__(self, data):
        if isinstance(data, str) or isinstance(data, unicode):
            return RestResponse.loads(data)
        else:
            return RestResponse.parse(data)

    @staticmethod
    def parse(data, parent=None):
        if isinstance(data, dict):
            return RestObject(data, parent=parent)
        elif isinstance(data, list):
            return RestList(data, parent=parent)
        elif isinstance(data, type(None)):
            return RestObject({}, parent=parent)
        elif isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, str) and not istext(data):
            return '__binary__: %s' % base64.b64encode(data)
        elif callable(data):
            return '__callable__: %s' % base64.b64encode(pickle.dumps(data))
        else:
            return data

    @staticmethod
    def loads(data):
        try:
            data = json.loads(data)
        except Exception:
            raise ValueError('RestResponse data must be JSON deserializable')

        return RestResponse.parse(data)
