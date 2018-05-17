import RestResponse
import requests


def test_none_prop():
    obj = RestResponse.parse({})
    assert not obj.missing_prop
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
        'new_field': 'Test New Field'
    })
    r = requests.put('http://jsonplaceholder.typicode.com/users/{0}'.format(user.id), json=user)
    assert r.ok
    user = RestResponse.parse(r.json())
    assert user.name == 'Test New Name'
    assert user.new_field == 'Test New Field'
    for key in user:
        assert key in user.keys()
    user.clear()
    assert len(user) == 0
