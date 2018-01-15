import json
import simplejson


class RestEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, RestObject) or isinstance(obj, RestList):
            return getattr(obj.__class__, '__repr__', super(RestEncoder, self).encode)(obj)
        else:
            return super(RestEncoder, self).encode(obj)


json._default_encoder = RestEncoder()
simplejson._default_encoder = RestEncoder()


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


class RestList(list):
    def __init__(self, data):
        if not isinstance(data, list):
            raise ValueError('RestList must be list object')

        for item in data:
            self.append(item)

    def pretty_print(self, indent=4):
        return json.dumps([x.__repr_data__ if hasattr(x, '__repr_data__') else x for x in self], indent=indent)

    def __repr__(self):
        return json.dumps([x.__repr_data__ if hasattr(x, '__repr_data__') else x for x in self])

    def append(self, item):
        if isinstance(item, dict):
            super(RestList, self).append(RestObject(item))
        elif isinstance(item, list):
            super(RestList, self).append(RestList(item))
        else:
            super(RestList, self).append(item)


class RestObject(dict):
    def __init__(self, data):
        if not isinstance(data, dict):
            raise ValueError('RestObject data must be dict object')
        self.__data__ = {}
        self.__repr_data__ = data
        for k, v in data.iteritems():
            self.__data__[k] = self._init_data(v)

    def __repr__(self):
        return json.dumps(self.__repr_data__)

    def __str__(self):
        return json.dumps(self.__repr_data__)

    def pretty_print(self, indent=4):
        return json.dumps(self.__repr_data__, indent=indent)

    @property
    def __dict__(self):
        return self.__repr_data__

    def __dir__(self):
        return dir(self.__repr_data__)

    def __iter__(self):
        for x in self.keys():
            yield x

    def __eq__(self, other):
        if type(other) == type(self):
            return self.__repr_data__ == other.__repr_data__
        else:
            return False

    def __getattr__(self, name):
        if name in self.__data__:
            return self.__data__.get(name)
        else:
            return NoneProp(self, name)

    def __setattr__(self, name, value):
        if name == '__data__' or name == '__repr_data__':
            super(RestObject, self).__setattr__(name, value)
        else:
            self._update_object({name: value})

    def keys(self):
        return self.__repr_data__.keys()

    def get(self, key, default=None):
        return self.__repr_data__.get(key, default)

    def has_key(self, key):
        return self.__repr_data__.has_key(key)

    def items(self):
        return self.__repr_data__.items()

    def iteritems(self):
        return self.__repr_data__.iteritems()

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

    def _init_data(self, v):
        if isinstance(v, dict):
            return RestObject(v)
        elif isinstance(v, list):
            return RestList(v)
        else:
            return v

    def _update_object(self, data):
        self.__repr_data__.update(data)
        for k, v in data.iteritems():
            self.__data__[k] = self._init_data(v)


class RestResponse(object):
    @staticmethod
    def parse(data):
        try:
            json.dumps(data)
        except Exception:
            raise ValueError('RestResponse data must be JSON serializable')

        if isinstance(data, dict):
            return RestObject(data)
        elif isinstance(data, list):
            return RestList(data)
        else:
            return data
