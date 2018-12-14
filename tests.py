import sys
import RestResponse
import requests
from datetime import datetime
from decimal import Decimal
import base64
import json
import cloudpickle as pickle


def test_none_prop():
    obj = RestResponse.parse({})
    assert not obj.missing_prop
    assert not obj.missing_prop_call()
    assert isinstance(obj.prop, RestResponse.NoneProp)


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
    obj.nested.prop = None
    assert isinstance(obj.nested, RestResponse.RestObject)
    assert 'prop' in obj.nested
    assert 'prop' in obj.nested.keys()
    assert 'prop' in dir(obj.nested)


def test_rest_list():
    lst = RestResponse.parse([])
    assert isinstance(lst, RestResponse.RestList)
    lst.append('item')
    assert 'item' in lst
    assert len(lst) == 1
    assert lst.pop() == 'item'
    assert len(lst) == 0


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
        'binary': requests.get('https://picsum.photos/1').content,
        'callable': lambda x: x + 1
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
    for key in user:
        assert key in user.keys()
    user.clear()
    assert len(user) == 0


def test_supported_encoder_types():
    d1 = datetime.utcnow()
    d2 = d1.date()
    decimal = Decimal('3.1459')
    binary = requests.get('https://picsum.photos/1').content

    data = RestResponse.parse({
        'datetime': d1,
        'date': d2,
        'decimal': decimal,
        'binary': binary,
        'callable': lambda x: x + 1
    })

    assert data.datetime == d1
    assert data.date == d2
    assert data.decimal == float(Decimal('3.1459'))
    assert data.binary == binary
    assert data.callable(1) == 2

    raw = json.loads(repr(data))
    assert raw['binary'].startswith('__binary__: ')
    if sys.version_info[0] < 3:
        assert base64.b64decode(raw['binary'].replace('__binary__: ', '')) == binary
    else:
        assert base64.b64decode(raw['binary'].replace('__binary__: b', '')) == binary
    assert raw['callable'].startswith('__callable__: ')
    if sys.version_info[0] < 3:
        assert pickle.loads(base64.b64decode(raw['callable'].replace('__callable__: ', ''))).func_code == \
            data.callable.func_code
        assert pickle.loads(base64.b64decode(raw['callable'].replace('__callable__: ', '')))(1) == 2
    else:
        assert pickle.loads(base64.b64decode(raw['callable'].replace('__callable__: b', ''))).__code__ == \
            data.callable.__code__
        assert pickle.loads(base64.b64decode(raw['callable'].replace('__callable__: b', '')))(1) == 2
