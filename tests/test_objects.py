import pytest
import RestResponse
import requests
from datetime import datetime, date
from decimal import Decimal
import json
from tests.models import DBModel, Model, Ref, OverridesModel


def test_none_prop():
    obj = RestResponse.parse({})
    assert not obj.missing_prop
    obj.none_prop['test'] = 'this'
    assert obj.none_prop.test == 'this'
    assert isinstance(obj.prop, RestResponse.NoneProp)
    assert 'test' not in obj.missing_prop
    assert [x for x in obj.missing_prop] == []
    for none in obj.missing_prop:
        raise AssertionError('NoneProp should have nothing to yield')


def test_rest_obj(binary):
    obj = RestResponse.parse({})
    assert isinstance(obj, RestResponse.RestObject)
    obj.id = 1
    assert 'id' in obj
    assert 'id' in obj.keys()
    assert len(obj) == 1
    assert obj.pop('id') == 1
    assert obj.pop('foo') is None
    assert obj.pop('foo', 'bar') == 'bar'
    assert len(obj) == 0
    obj.id = 1
    assert obj.popitem() == ('id', 1)
    assert len(obj) == 0
    obj.nested.prop = None
    assert isinstance(obj.nested, RestResponse.RestObject)
    assert 'prop' in obj.nested
    assert 'prop' in obj.nested.keys()
    obj.update(RestResponse.parse({
        'test': 'this',
        'callable': lambda x: x + 1,
        'binary': binary
    }))
    assert obj.test == 'this'
    assert obj.callable(1) == 2
    assert not RestResponse.utils.istext(obj.binary)
    obj.restobj = RestResponse.parse({
        'test': 'this',
        'callable': lambda x: x + 1
    })
    assert obj.restobj.test == 'this'
    assert obj.restobj.callable(1) == 2
    obj.none_prop = obj.missing_prop
    assert obj().get('none_prop') is None
    assert obj['test'] == 'this'
    assert isinstance(obj['missing_key'], RestResponse.NoneProp)
    obj['key'] = obj.restobj
    assert obj['key'].test == 'this' == obj.key.test == obj['key']['test']
    assert obj['key'].callable(1) == 2
    obj['new_key'].some_prop = [1]
    assert len(obj.new_key.some_prop) == 1


def test_callable():
    base = RestResponse.parse({
        'trigger': lambda x: x + 1
    })
    t = RestResponse.parse(base())
    assert t.trigger(1) == 2
    t = RestResponse.loads(base.pretty_print())
    assert t.trigger(1) == 2


def test_binary(binary):
    base = RestResponse.parse({
        'binary': binary
    })
    t = RestResponse.parse(base())
    assert t.binary == binary
    t = RestResponse.loads(base.pretty_print())
    assert t.binary == binary


def test_rest_list(binary):
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
    assert lst.pop() == b'byte string'
    assert lst.pop() == u'\U0001f44d'
    lst.append(RestResponse.parse({
        'test': 'RestObj',
        'callable': lambda x: x + 1,
        'binary': binary,
        'unicode': u'\U0001f44d',
        'bytes': b'byte string'
    }))
    assert lst[-1].test == 'RestObj'
    assert lst[-1].callable(1) == 2
    assert lst[-1].unicode == u'\U0001f44d'
    assert lst[-1].bytes == b'byte string'
    assert not RestResponse.utils.istext(lst[-1].binary)
    lst.append(RestResponse.parse([lst[-1]]))
    assert isinstance(lst[-1], RestResponse.RestList)
    assert isinstance(lst[-1][-1], RestResponse.RestObject)
    lst.insert(0, RestResponse.parse({
        'test': 'RestObj',
        'callable': lambda x: x + 1,
        'binary': binary,
        'unicode': u'\U0001f44d'
    }))
    assert lst[0].test == 'RestObj'
    assert lst[0].callable(1) == 2
    assert lst[0].unicode == u'\U0001f44d'
    assert not RestResponse.utils.istext(lst[0].binary)
    lst.append(lst[0].none_prop)
    assert lst()[-1] is not None

    lst[0] = {
        'id': 1,
        'foo': 'bar'
    }
    assert isinstance(lst[0], RestResponse.RestObject)

    with pytest.raises(IndexError):
        lst[100] = 'foo'

    data = {
        'lst': ['test', 'encodedness']
    }
    obj = RestResponse.parse(data)
    assert obj.lst == data['lst']

    lst = RestResponse.parse(['foo'])
    lst[-1] = ['foo', {'foo': 'bar'}]
    assert isinstance(lst[-1], RestResponse.RestList)
    assert isinstance(lst[-1][-1], RestResponse.RestObject)


def test_pretty_print(requests_mock, user_text):
    requests_mock.get('http://jsonplaceholder.typicode.com/users/1', text=user_text)
    r = requests.get('http://jsonplaceholder.typicode.com/users/1')
    user = RestResponse.parse(r.json())
    assert len(user.pretty_print().split('\n')) == len(r.text.split('\n'))


def test_encode_on_request(binary, requests_mock, user_text):
    requests_mock.get('http://jsonplaceholder.typicode.com/users/1', text=user_text)
    r = requests.get('http://jsonplaceholder.typicode.com/users/1')
    user = RestResponse.parse(r.json())
    user.update({
        'name': 'Test New Name',
        'new_field': 'Test New Field',
        'binary': binary,
        'callable': lambda x: x + 1,
        'unicode': u'\U0001f44d'
    })

    requests_mock.put('http://jsonplaceholder.typicode.com/users/{0}'.format(user.id), text=repr(user))
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
    assert user.unicode == u'\U0001f44d'
    for key in user:
        assert key in user.keys()
    user.clear()
    assert len(user) == 0


def test_supported_encoder_types(binary):
    d1 = datetime.utcnow()
    d2 = d1.date()
    decimal = Decimal('3.1459')

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
    assert isinstance(data.decimal, Decimal)
    assert float(data.decimal) == float(Decimal('3.1459'))
    assert data.binary == binary
    assert data.callable(1) == 2
    assert data.unicode == u'\U0001f44d'
    assert data.ascii_unicode == u'test'

    raw = json.loads(repr(data))
    assert raw['binary'].startswith('__binary__: ')
    assert RestResponse.utils._decode_binary(raw['binary']) == binary
    assert raw['callable'].startswith('__callable__: ')
    func = RestResponse.utils._decode_callable(raw['callable'])
    assert func.__code__ == data.callable.__code__
    assert func(1) == 2
    assert raw['ascii_unicode'] == 'test'


def test_orm_sqlalchemy(db, db_model, binary):
    d1 = datetime.utcnow()
    d2 = d1.date()
    decimal = Decimal('3.1459')
    db_model.data = RestResponse.parse({
        'datetime': d1,
        'date': d2,
        'decimal': decimal,
        'binary': binary,
        'callable': lambda x: x + 1,
        'unicode': u'\U0001f44d',
        'ascii_unicode': u'test'
    })

    db.session.add(db_model)
    db.session.commit()

    session = db.create_scoped_session(dict(expire_on_commit=False))
    committed = session.query(DBModel).first()

    assert committed.data.datetime == RestResponse.utils.encode_item(d1)
    assert committed.data.date == RestResponse.utils.encode_item(d2)
    assert committed.data.decimal == float(Decimal('3.1459'))
    assert committed.data.binary == binary
    assert committed.data.callable(1) == 2
    assert committed.data.unicode == u'\U0001f44d'
    assert committed.data.ascii_unicode == u'test'

    db_model.data = {}
    db.session.commit()

    session = db.create_scoped_session(dict(expire_on_commit=False))
    committed = session.query(DBModel).first()

    assert isinstance(committed.data, RestResponse.RestObject)

    db_model.data = []
    db.session.commit()

    session = db.create_scoped_session(dict(expire_on_commit=False))
    committed = session.query(DBModel).first()

    assert isinstance(committed.data, RestResponse.RestList)

    db_model.data = None
    db.session.commit()

    session = db.create_scoped_session(dict(expire_on_commit=False))
    committed = session.query(DBModel).first()

    assert isinstance(committed.data, RestResponse.RestObject)


def test_api_model(binary):
    model = OverridesModel({
        '_foo': 'bar',
        'foo': 'bar'
    })

    assert '_foo' in model._data
    assert 'foo' not in model._data
    assert model._foo == 'bar'

    Model.__opts__.update({
        'encode_binary': False,
        'encode_callable': False,
        'decode_binary': False,
        'decode_callable': False,
        '_overrides': ['_foo']
    })

    d = datetime.utcnow()
    d2 = d.date()
    model = Model({
        'id': 5,
        'string': 'foo',
        'floating_point': float(4.0),
        'date_time': d,
        'date': d2,
        'ref': {
            'id': 5,
            'string': 'string',
            'foo': 'bar'
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
        ],
        'foo': 'bar',
        '_foo': 'bar',
        '_bar': 'foo'
    })

    model2 = Model({
        'id': 5,
        'string': 'foo',
        'floating_point': float(4.0),
        'date_time': d,
        'date': d2,
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
        ],
        'foo': 'bar',
        '_foo': 'bar',
        '_bar': 'foo'
    })

    with pytest.raises(AssertionError):
        assert model == model2

    assert bool(model2.ref) is False

    model2.ref = Ref({
        'id': 5,
        'string': 'string',
        'foo': 'bar'
    })

    assert model == model2

    as_dict = model._as_json
    repr(as_dict)
    assert as_dict['id'] == 5
    assert as_dict['string'] == 'foo'
    assert as_dict['floating_point'] == float(4.0)
    assert as_dict['date_time'] == Model.__opts__['encode_datetime'](d)
    assert as_dict['date'] == Model.__opts__['encode_date'](d2)

    model = Model(as_dict)

    assert 'foo' not in model._data
    assert 'foo' not in model.ref._data
    assert '_bar' not in model._data
    assert '_foo' in model._data
    assert model._foo == 'bar'
    assert isinstance(model.id, int)
    assert model.id == 5
    assert isinstance(model.string, str)
    assert model.string == 'foo'
    assert isinstance(model.floating_point, float)
    assert model.floating_point == float(4.0)
    assert isinstance(model.date_time, datetime)
    assert model.date_time == d.replace(microsecond=0)
    assert isinstance(model.date, date)
    assert model.date == d2
    assert isinstance(model.ref, Ref)
    assert model.ref.id == 5
    assert model.ref.string == 'string'
    assert isinstance(model.int_collection, list)
    assert len(model.int_collection) == 3
    for ref in model.ref_collection:
        assert isinstance(ref, Ref)

    model.id = 10
    assert model.id == 10
    model.string = 'bar'
    assert model.string == 'bar'
    model.floating_point = Decimal(5.3)
    assert model.floating_point == float(5.3)

    model.int_collection.append(1337)
    assert 1337 in model.int_collection
    model.ref_collection.append(Ref({
        'id': 1337,
        'string': 'foo'
    }))
    assert model.ref_collection[-1].id == 1337
    assert model.ref_collection[-1].string == 'foo'

    model.id = '5'
    assert model.id == 5
    with pytest.raises(ValueError):
        model.id = 'test'

    model.id_doesnt_raise = 'test'
    assert model.id_doesnt_raise is None

    with pytest.raises(ValueError):
        model.string = 5

    model.string_doesnt_raise = 5
    assert model.string_doesnt_raise == '5'

    with pytest.raises(ValueError):
        model.floating_point = 'test'

    model.floating_point_doesnt_raise = 'test'
    assert model.floating_point_doesnt_raise is None

    with pytest.raises(ValueError):
        model.func = lambda x: x + 1
        as_dict = model._as_json

    model.binary = binary

    with pytest.raises(ValueError):
        as_dict = model._as_json

    with pytest.raises(ValueError):
        model.int_collection.append('test')

    with pytest.raises(ValueError):
        model.ref_collection.append('test')

    Model.__opts__.update({
        'encode_binary': True,
        'encode_callable': True,
        'decode_binary': True,
        'decode_callable': True
    })

    model = Model({
        'binary': binary,
        'func': lambda x: x + 1
    })

    as_dict = model._as_json
    assert isinstance(as_dict, dict)
    assert RestResponse.utils._decode_binary(as_dict.get('binary')) == model.binary

    func = RestResponse.utils._decode_callable(as_dict.get('func'))
    assert func.__code__ == model.func.__code__


def test_api_collection():
    models = RestResponse.ApiCollection(Model, [{
        'id': 5,
        'string': 'foo',
        'floating_point': float(4.0),
        'ref': {
            'id': 5,
            'string': 'string',
            'foo': 'bar'
        },
        'int_collection': [1, 2, 3],
        'int_collection_doesnt_raise': ['test'],
        'ref_collection': [
            {
                'id': 1,
                'string': 'string'
            },
            {
                'id': 2,
                'string': 'string'
            }
        ],
        'foo': 'bar'
    } for x in range(3)])

    with pytest.raises(ValueError):
        models[0].int_collection.append('test')

    assert len(models[0].int_collection_doesnt_raise) == 0
    models[0].int_collection_doesnt_raise.append('test')
    assert len(models[0].int_collection_doesnt_raise) == 0
    models[0].int_collection_doesnt_raise.append(5)
    assert models[0].int_collection_doesnt_raise[0] == 5

    assert len(models) == 3
    as_list = models._as_json
    assert isinstance(as_list, list)

    for m in models:
        ref = Ref({
            'id': datetime.utcnow().strftime('%s'),
            'string': datetime.utcnow().isoformat()
        })
        m.ref_collection.append(ref)
        assert m.ref_collection[-1].id == ref.id
        assert m.ref_collection[-1].string == ref.string


def test_default():
    obj = RestResponse.parse({
        'callable': lambda x: x + 1
    })

    data = RestResponse.RestEncoder().default(obj)
    assert data['callable'].startswith('__callable__')
    assert RestResponse.utils.decode_item(data['callable'])(2) == 3

    data = RestResponse.RestEncoderSimple().default(obj)
    assert data['callable'].startswith('__callable__')
    assert RestResponse.utils.decode_item(data['callable'])(2) == 3

    obj = RestResponse.parse([
        lambda x: x + 1
    ])

    data = RestResponse.RestEncoder().default(obj)
    assert data[0].startswith('__callable__')
    assert RestResponse.utils.decode_item(data[0])(2) == 3

    data = RestResponse.RestEncoderSimple().default(obj)
    assert data[0].startswith('__callable__')
    assert RestResponse.utils.decode_item(data[0])(2) == 3

    assert obj.__json__() == data
