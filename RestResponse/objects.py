import json
import simplejson
import six
from datetime import datetime
from sqlalchemy.ext.mutable import Mutable
from RestResponse import utils


class ApiModel(object):
    __opts__ = {
        'encode_binary': False,
        'encode_callable': False,
        'decode_binary': False,
        'decode_callable': False
    }

    @property
    def _data(self):
        return self.__data

    @_data.setter
    def _data(self, data):
        self.__data = data = data or RestResponse.parse({}, **self.__opts__)
        if isinstance(data, dict) or isinstance(data, list):
            self.__data = RestResponse.parse(data, **self.__opts__)
        elif isinstance(data, str) or not utils.PYTHON3 and isinstance(data, unicode):
            self.__data = RestResponse.loads(data or "{}", **self.__opts__)
        elif isinstance(data, ApiModel):
            self.__data = data._data

    def _to_dict(self):
        return self._data()

    def _format_datetime(self, d, format='%Y-%m-%dT%H:%M:%SZ'):
        if not isinstance(d, datetime):
            try:
                return datetime.strptime(d, format)
            except ValueError:
                return None
        else:
            return d


class RestEncoder(utils.CustomObjectEncoder):
    __opts__ = {
        'encode_binary': True,
        'encode_callable': True,
        'decode_binary': True,
        'decode_callable': True
    }

    def isinstance(self, obj, cls):
        if isinstance(obj, (RestResponseObj, NoneProp)):
            if isinstance(obj, RestResponseObj):
                self.__opts__.update(obj.__opts__)
            return False
        return isinstance(obj, cls)

    def _walk_dict(self, obj):
        result = {}
        for k, v in six.iteritems(obj):
            if isinstance(v, NoneProp):
                result[k] = None
            elif isinstance(v, dict):
                result[k] = self._walk_dict(v)
            elif isinstance(v, list):
                result[k] = self._recurse_list(v)
            else:
                result[k] = utils.encode_item(v, **self.__opts__)
        return result

    def _recurse_list(self, obj):
        result = []
        for item in obj:
            if isinstance(item, NoneProp) or item is None:
                result.append(None)
            elif isinstance(item, list):
                result.append(self._recurse_list(item))
            elif isinstance(item, dict):
                result.append(self._walk_dict(item))
            else:
                result.append(utils.encode_item(item, **self.__opts__))
        return result

    def default(self, obj):
        if isinstance(obj, ApiModel):
            return self.default(obj._data)
        if isinstance(obj, list):
            return self._recurse_list(obj)
        elif isinstance(obj, dict):
            return self._walk_dict(obj)
        elif isinstance(obj, NoneProp) or obj is None:
            return None
        else:
            return utils.encode_item(obj, **self.__opts__)


json._default_encoder = RestEncoder()
simplejson._default_encoder = RestEncoder()


class RestResponseObj(Mutable, object):
    __parent__ = None
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

    def __iter__(self):
        for i in []:
            yield i

    def __contains__(self, key):
        return False

    def __unicode__(self):
        return u'None'

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

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)


class RestList(RestResponseObj, list):
    def __init__(self, data, parent=None, **kwargs):
        if not isinstance(data, list):
            raise ValueError('RestList data must be list object')

        self.__parent__ = parent
        self.__opts__.update(kwargs)

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
        return utils.decode_item(item, **self.__opts__)

    def __contains__(self, item):
        if not (isinstance(item, RestResponseObj) or isinstance(item, NoneProp)):
            item = utils.encode_item(item, **self.__opts__)
        return super(RestList, self).__contains__(item)

    def __iter__(self):
        for item in list.__iter__(self):
            yield utils.decode_item(item, **self.__opts__)

    def append(self, item):
        if not (isinstance(item, RestResponseObj) or isinstance(item, NoneProp)):
            utils.encode_item(item, **self.__opts__)
        super(RestList, self).append(RestResponse.parse(item, parent=self))
        self.changed()

    def extend(self, items):
        for item in items:
            self.append(item)

    def insert(self, index, item):
        if not (isinstance(item, RestResponseObj) or isinstance(item, NoneProp)):
            utils.encode_item(item, **self.__opts__)
        super(RestList, self).insert(index, RestResponse.parse(item, parent=self))
        self.changed()

    def pop(self, index=None):
        if index:
            value = super(RestList, self).pop(index)
        else:
            value = super(RestList, self).pop()
        self.changed()
        return utils.decode_item(value, **self.__opts__)

    def remove(self, item):
        super(RestList, self).remove(item)
        self.changed()


class RestObject(RestResponseObj, dict):
    def __init__(self, data, parent=None, **kwargs):
        if not isinstance(data, dict):
            raise ValueError('RestObject data must be dict object')
        self.__data__ = {}
        self.__parent__ = parent
        self.__opts__.update(kwargs)

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
        return dir(self.__data__) + list(self.keys())

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

    def popitem(self):
        key_value = self.__data__.popitem()
        self.changed()
        return key_value

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

    def __getitem__(self, name):
        return self.__data__.__getitem__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)

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
            return RestObject(v, parent=self, **self.__opts__)
        elif isinstance(v, list) and not isinstance(v, RestList):
            return RestList(v, parent=self, **self.__opts__)
        else:
            return utils.decode_item(v, **self.__opts__)

    def _update_object(self, data):
        for k, v in six.iteritems(data):
            self.__data__[k] = self._init_data(v)
        self.changed()


class RestResponse(object):
    def __new__(self, data, **kwargs):
        if isinstance(data, str) or not utils.PYTHON3 and isinstance(data, unicode):
            return RestResponse.loads(data, **kwargs)
        else:
            return RestResponse.parse(data, **kwargs)

    @staticmethod
    def parse(data, parent=None, **kwargs):
        if isinstance(data, RestResponseObj) or isinstance(data, NoneProp):
            return data
        elif isinstance(data, dict):
            return RestObject(data, parent=parent, **kwargs)
        elif isinstance(data, list):
            return RestList(data, parent=parent, **kwargs)
        elif isinstance(data, type(None)):
            return RestObject({}, parent=parent, **kwargs)
        else:
            return utils.encode_item(data, **kwargs)

    @staticmethod
    def loads(data, **kwargs):
        try:
            data = json.loads(data)
        except Exception:
            raise ValueError('RestResponse data must be JSON deserializable')

        return RestResponse.parse(data, **kwargs)
