from __future__ import division, absolute_import, print_function, unicode_literals

import json
import simplejson
import six
from decimal import Decimal
from sqlalchemy.ext.mutable import Mutable


class RestEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        try:
            super(RestEncoder, self).__init__(*args, **kwargs)
        except TypeError:
            super(RestEncoder, self).__init__()

    def _walk_dict(self, obj):
        result = {}
        for k, v in six.iteritems(obj):
            if isinstance(v, RestResponseObj):
                result[k] = v.__repr_data__
            elif isinstance(v, dict):
                result[k] = self._walk_dict(v)
            elif isinstance(v, list):
                result[k] = self._recurse_list(v)
            elif isinstance(v, Decimal):
                result[k] = float(v)
            else:
                if isinstance(v, NoneProp):
                    v = None
                result[k] = v

        return result

    def _recurse_list(self, obj):
        result = []
        for item in obj:
            if isinstance(item, RestResponseObj):
                result.append(item.__repr_data__)
            elif isinstance(item, list):
                result.append(self._recurse_list(item))
            elif isinstance(item, dict):
                result.append(self._walk_dict(item))
            elif isinstance(item, Decimal):
                result.append(float(item))
            else:
                if isinstance(item, NoneProp):
                    item = None
                result.append(item)

        return result

    def encode(self, obj):
        if isinstance(obj, RestResponseObj):
            return getattr(obj.__class__, '__repr__', super(RestEncoder, self).encode)(obj)
        elif isinstance(obj, list):
            obj = self._recurse_list(obj)
        elif isinstance(obj, dict):
            obj = self._walk_dict(obj)
        elif isinstance(obj, NoneProp):
            obj = None
        elif isinstance(obj, Decimal):
            return float(obj)

        return super(RestEncoder, self).encode(obj)


json._default_encoder = RestEncoder()
simplejson._default_encoder = RestEncoder()


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
    def __repr_data__(self):
        return json.loads(self.pretty_print())

    def pretty_print(self, indent=4):
        return json.dumps(self, indent=indent)

    def __repr__(self):
        return super(RestList, self).__repr__()

    def append(self, item):
        super(RestList, self).append(RestResponse.parse(item, parent=self))
        self.changed()

    def extend(self, items):
        for item in items:
            self.append(item)

    def insert(self, index, item):
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
        return self.pretty_print(indent=None)

    def __str__(self):
        return self.pretty_print(indent=None)

    def __contains__(self, key):
        return key in self.__data__

    def __len__(self):
        return len(self.__data__)

    @property
    def __repr_data__(self):
        return json.loads(json.dumps(self.__data__))

    def pretty_print(self, indent=4):
        return json.dumps(self.__data__, indent=indent)

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
            return self.__repr_data__ == other.__repr_data__
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
        return self.__repr_data__.keys()

    def get(self, key, default=None):
        return self.__repr_data__.get(key, default)

    def has_key(self, key):
        return key in self.__repr_data__

    def items(self):
        return self.__repr_data__.items()

    def iteritems(self):
        return six.iteritems(self.__repr_data__)

    def iterkeys(self):
        return self.__repr_data__.iterkeys()

    def itervalues(self):
        return self.__repr_data__.itervalues()

    def values(self):
        return self.__repr_data__.values()

    def viewitems(self):
        return self.__repr_data__.viewitems()

    def viewkeys(self):
        return self.__repr_data__.viewkeys()

    def viewvalues(self):
        return self.__repr_data__.viewvalues()

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
        return v

    def _update_object(self, data):
        for k, v in six.iteritems(data):
            self.__data__[k] = self._init_data(v)
        self.changed()


class RestResponse(object):
    @staticmethod
    def parse(data, parent=None):
        try:
            data = json.loads(json.dumps(data))
        except Exception:
            raise ValueError('RestResponse data must be JSON serializable')

        if isinstance(data, dict):
            return RestObject(data, parent=parent)
        elif isinstance(data, list):
            return RestList(data, parent=parent)
        elif isinstance(data, type(None)):
            return RestObject({}, parent=parent)
        elif isinstance(data, Decimal):
            return float(data)
        else:
            return data
