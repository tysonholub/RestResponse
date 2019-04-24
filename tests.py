import RestResponse
import requests
from datetime import datetime
from decimal import Decimal
import json


class Ref(RestResponse.ApiModel):
    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return int(self._data.id)

    @id.setter
    def id(self, id):
        self._data.id = int(id)

    @property
    def string(self):
        return str(self._data.string)

    @string.setter
    def string(self, string):
        self._data.string = str(string)


class Model(RestResponse.ApiModel):
    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return int(self._data.id)

    @id.setter
    def id(self, id):
        self._data.id = int(id)

    @property
    def string(self):
        return str(self._data.string)

    @string.setter
    def string(self, string):
        self._data.string = str(string)

    @property
    def floating_point(self):
        return float(self._data.floating_point)

    @floating_point.setter
    def floating_point(self, floating_point):
        self._data.floating_point = float(floating_point)

    @property
    def date_time(self):
        return self._format_datetime(self._data.date_time)

    @date_time.setter
    def date_time(self, date_time):
        self._data.date_time = self._format_datetime(date_time)

    @property
    def func(self):
        return self._data.func

    @func.setter
    def func(self, func):
        self._data.func = func

    @property
    def binary(self):
        return self._data.binary

    @binary.setter
    def binary(self, binary):
        self._data.binary = binary

    @property
    def ref(self):
        if not self._data.ref:
            self._data.ref = Ref()
        return Ref(self._data.ref)

    @ref.setter
    def ref(self, ref):
        self._data.ref = Ref(ref)

    @property
    def int_collection(self):
        if not self._data.int_collection:
            self._data.int_collection = []
        return [int(x) for x in self._data.int_collection]

    @int_collection.setter
    def int_collection(self, int_collection):
        self._data.int_collection = [int(x) for x in self._data.int_collection]

    @property
    def ref_collection(self):
        if not self._data.ref_collection:
            self._data.ref_collection = []
        return [Ref(x) for x in self._data.ref_collection]

    @ref_collection.setter
    def ref_collection(self, ref_collection):
        self._data.ref_collection = [Ref(x) for x in self._data.ref_collection]


def test_api_model():
    d = datetime.utcnow()
    model = Model({
        'id': 5,
        'string': 'foo',
        'floating_point': float(4.0),
        'date_time': d,
        'ref': {
            'id': 5,
            'string': 'string'
        },
        'int_collection': [1, 2, 3],
        'ref_collection': [
            {
                'id': 1,
                'string': 'string'
            },
            {
                'id': 2,
                'string': 'string'
            }
        ]
    })

    assert isinstance(model.id, int)
    assert model.id == 5
    assert isinstance(model.string, str)
    assert model.string == 'foo'
    assert isinstance(model.floating_point, float)
    assert model.floating_point == float(4.0)
    assert isinstance(model.date_time, datetime)
    assert model.date_time == d
    assert isinstance(model.ref, Ref)
    assert model.ref.id == 5
    assert model.ref.string == 'string'
    assert isinstance(model.int_collection, list)
    assert len(model.int_collection) == 3
    for ref in model.ref_collection:
        assert isinstance(ref, Ref)
    as_dict = model._to_dict()
    assert as_dict['id'] == 5
    assert as_dict['string'] == 'foo'
    assert as_dict['floating_point'] == float(4.0)
    assert as_dict['date_time'] == d.isoformat()

    model.id = 10
    assert model.id == 10
    model.string = 'bar'
    assert model.string == 'bar'
    model.floating_point = Decimal(5.3)
    assert model.floating_point == float(5.3)

    try:
        model.id = '5'
        assert model.id == 5
        model.id = 'test'
        assert False
    except Exception as e:
        assert isinstance(e, ValueError)

    model.string = 5
    assert model.string == '5'

    try:
        model.floating_point = 'test'
        assert False
    except Exception as e:
        assert isinstance(e, ValueError)

    try:
        model.func = lambda x: x + 1
        as_dict = model._to_dict()
    except Exception as e:
        assert isinstance(e, ValueError)

    try:
        model.binary = requests.get('https://cataas.com/cat').content
        as_dict = model._to_dict()
    except Exception as e:
        if RestResponse.utils.PYTHON3:
            assert isinstance(e, ValueError)
        else:
            assert isinstance(e, UnicodeDecodeError)

    Model.__opts__ = {
        'encode_binary': True,
        'encode_callable': True,
        'decode_binary': True,
        'decode_callable': True
    }

    model = Model({
        'binary': requests.get('https://cataas.com/cat').content,
        'func': lambda x: x + 1
    })

    as_dict = model._to_dict()
    assert RestResponse.utils._decode_binary(as_dict.get('binary')) == model.binary

    func = RestResponse.utils._decode_callable(as_dict.get('func'))
    if not RestResponse.utils.PYTHON3:
        assert func.func_code == model.func.func_code
    else:
        assert func.__code__ == model.func.__code__


def test_none_prop():
    obj = RestResponse.parse({})
    assert not obj.missing_prop
    assert not obj.missing_prop_call()
    obj.none_prop['test'] = 'this'
    assert obj.none_prop.test == 'this'
    assert isinstance(obj.prop, RestResponse.NoneProp)
    assert 'test' not in obj.missing_prop
    assert [x for x in obj.missing_prop] == []
    for none in obj.missing_prop:
        raise AssertionError('NoneProp should have nothing to yield')


def test_rest_obj():
    obj = RestResponse.parse({})
    assert isinstance(obj, RestResponse.RestObject)
    obj.id = 1
    assert 'id' in obj
    assert 'id' in obj.keys()
    assert 'id' in dir(obj)
    assert len(obj) == 1
    assert obj.pop('id') == 1
    assert len(obj) == 0
    obj.id = 1
    assert obj.popitem() == ('id', 1)
    assert len(obj) == 0
    obj.nested.prop = None
    assert isinstance(obj.nested, RestResponse.RestObject)
    assert 'prop' in obj.nested
    assert 'prop' in obj.nested.keys()
    assert 'prop' in dir(obj.nested)
    obj.update(RestResponse.parse({
        'test': 'this',
        'callable': lambda x: x+1,
        'binary': requests.get('https://cataas.com/cat').content
    }))
    assert obj.test == 'this'
    assert obj.callable(1) == 2
    assert not RestResponse.utils.istext(obj.binary)
    obj.restobj = RestResponse.parse({
        'test': 'this',
        'callable': lambda x: x+1
    })
    assert obj.restobj.test == 'this'
    assert obj.restobj.callable(1) == 2
    obj.none_prop = obj.missing_prop
    assert obj().get('none_prop') is None
    assert obj['test'] == 'this'
    exc = None
    try:
        obj['missing_key']
    except Exception as e:
        exc = e
    assert isinstance(exc, KeyError)
    obj['key'] = obj.restobj
    assert obj['key'].test == 'this' == obj.key.test == obj['key']['test']
    assert obj['key'].callable(1) == 2


def test_callable():
    base = RestResponse.parse({
        'trigger': lambda x: x+1
    })
    t = RestResponse.parse(base())
    assert t.trigger(1) == 2
    t = RestResponse.loads(base.pretty_print())
    assert t.trigger(1) == 2


def test_binary():
    binary = requests.get('https://cataas.com/cat').content
    base = RestResponse.parse({
        'binary': binary
    })
    t = RestResponse.parse(base())
    assert t.binary == binary
    t = RestResponse.loads(base.pretty_print())
    assert t.binary == binary


def test_rest_list():
    lst = RestResponse.parse([])
    assert isinstance(lst, RestResponse.RestList)
    lst.append('item')
    assert 'item' in lst
    assert len(lst) == 1
    assert lst.pop() == 'item'
    lst.append(u'\U0001f44d')
    assert lst.pop(0) == u'\U0001f44d'
    assert len(lst) == 0
    lst.insert(0, u'\U0001f44d')
    lst.append(b'byte string')
    assert u'\U0001f44d' in lst
    assert b'byte string' in lst
    assert lst.pop() == 'byte string'
    assert lst.pop() == u'\U0001f44d'
    lst.append(RestResponse.parse({
        'test': 'RestObj',
        'callable': lambda x: x+1,
        'binary': requests.get('https://cataas.com/cat').content,
        'unicode': u'\U0001f44d',
        'bytes': b'byte string'
    }))
    assert lst[-1].test == 'RestObj'
    assert lst[-1].callable(1) == 2
    assert lst[-1].unicode == u'\U0001f44d'
    assert lst[-1].bytes == 'byte string'
    assert not RestResponse.utils.istext(lst[-1].binary)
    lst.append(RestResponse.parse([lst[-1]]))
    assert isinstance(lst[-1], RestResponse.RestList)
    assert isinstance(lst[-1][-1], RestResponse.RestObject)
    lst.insert(0, RestResponse.parse({
        'test': 'RestObj',
        'callable': lambda x: x+1,
        'binary': requests.get('https://cataas.com/cat').content,
        'unicode': u'\U0001f44d'
    }))
    assert lst[0].test == 'RestObj'
    assert lst[0].callable(1) == 2
    assert lst[0].unicode == u'\U0001f44d'
    assert not RestResponse.utils.istext(lst[0].binary)
    lst.append(lst[0].none_prop)
    assert lst()[-1] is None


def test_pretty_print():
    r = requests.get('http://jsonplaceholder.typicode.com/users/1')
    user = RestResponse.parse(r.json())
    assert len(user.pretty_print().split('\n')) == len(r.text.split('\n'))


def test_encode_on_request():
    r = requests.get('http://jsonplaceholder.typicode.com/users/1')
    user = RestResponse.parse(r.json())
    user.update({
        'name': 'Test New Name',
        'new_field': 'Test New Field',
        'binary': requests.get('https://cataas.com/cat').content,
        'callable': lambda x: x + 1,
        'unicode': u'\U0001f44d'
    })
    r = requests.put('http://jsonplaceholder.typicode.com/users/{0}'.format(user.id), json=user)
    assert r.ok
    r = requests.put('http://jsonplaceholder.typicode.com/users/{0}'.format(user.id), json=user())
    assert r.ok
    user = RestResponse.parse(r.json())
    assert user.name == 'Test New Name'
    assert user.new_field == 'Test New Field'
    user = RestResponse.loads(r.text)
    assert user.name == 'Test New Name'
    assert user.new_field == 'Test New Field'
    if RestResponse.utils.PYTHON34:
        assert user.unicode == u'\U0001f44d'.encode('utf-8')
    else:
        assert user.unicode == u'\U0001f44d'
    for key in user:
        assert key in user.keys()
    user.clear()
    assert len(user) == 0


def test_supported_encoder_types():
    d1 = datetime.utcnow()
    d2 = d1.date()
    decimal = Decimal('3.1459')
    binary = requests.get('https://cataas.com/cat').content

    data = RestResponse.parse({
        'datetime': d1,
        'date': d2,
        'decimal': decimal,
        'binary': binary,
        'callable': lambda x: x + 1,
        'unicode': u'\U0001f44d',
        'ascii_unicode': u'test'
    })

    assert data.datetime == d1
    assert data.date == d2
    assert data.decimal == float(Decimal('3.1459'))
    assert data.binary == binary
    assert data.callable(1) == 2
    assert data.unicode == u'\U0001f44d'
    assert data.ascii_unicode == u'test'

    raw = json.loads(repr(data))
    assert raw['binary'].startswith('__binary__: ')
    assert RestResponse.utils._decode_binary(raw['binary']) == binary
    assert raw['callable'].startswith('__callable__: ')
    func = RestResponse.utils._decode_callable(raw['callable'])
    if not RestResponse.utils.PYTHON3:
        assert func.func_code == data.callable.func_code
    else:
        assert func.__code__ == data.callable.__code__
    assert func(1) == 2
    assert raw['ascii_unicode'] == 'test'
