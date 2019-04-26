# RestResponse [![CircleCI](https://circleci.com/gh/tysonholub/RestResponse.svg?style=shield)](https://circleci.com/gh/tysonholub/RestResponse) [![PyPi](https://img.shields.io/badge/python-2.7%20%7C%203.4%20%7C%203.5%20%7C%203.6%20%7C%203.7-44CC11.svg)](https://pypi.org/project/RestResponse/) [![PyPiStats](https://img.shields.io/pypi/dm/restresponse.svg)](https://pypistats.org/packages/restresponse)

RestResponse aims to be a fluent python object for interfacing with RESTful JSON APIs

## Installation

Add this line to your application's requirements.txt:

```python
RestResponse
```

And then execute:

    $ pip install -r requirements.txt

Or install it yourself as:

    $ pip install RestResponse

## Usage

Import RestResponse and call parse on any list, dict, or primitive. You can also call loads on serialized json

```python
>>> import RestResponse
>>> import requests
>>> r = requests.get('http://jsonplaceholder.typicode.com/users')
>>> users = RestResponse.parse(r.json())
>>> # or
... users = RestResponse.loads(r.text)
>>> for user in users:
...     print user.name
...
Leanne Graham
Ervin Howell
Clementine Bauch
Patricia Lebsack
Chelsey Dietrich
Mrs. Dennis Schulist
Kurtis Weissnat
Nicholas Runolfsdottir V
Glenna Reichert
Clementina DuBuque
>>> user = users[0]
>>> print user.pretty_print(indent=4)
{
    "username": "Bret",
    "website": "hildegard.org",
    "name": "Leanne Graham",
    "company": {
        "bs": "harness real-time e-markets",
        "name": "Romaguera-Crona",
        "catchPhrase": "Multi-layered client-server neural-net"
    },
    "id": 1,
    "phone": "1-770-736-8031 x56442",
    "address": {
        "suite": "Apt. 556",
        "street": "Kulas Light",
        "geo": {
            "lat": "-37.3159",
            "lng": "81.1496"
        },
        "zipcode": "92998-3874",
        "city": "Gwenborough"
    },
    "email": "Sincere@april.biz"
}
>>> user.name = 'Rest Response'
>>> r = requests.put('http://jsonplaceholder.typicode.com/users/{0}'.format(user.id), json=user)
>>> # or if you choose to NOT allow by overriding
>>> # json._default_encoder = RestEncoder()
>>> # simplejson._default_encoder = RestEncoder()
>>> # use __call__ on RestResponseObj to explicitly dump and load via RestEncoder
>>> r = requests.put('http://jsonplaceholder.typicode.com/users/{0}'.format(user.id), json=user())  # Note __call__ on user
>>> response = RestResponse.parse(r.json())
>>> print response.name
Rest Response
>>> new = RestResponse.parse({})
>>> new.id = 5
>>> if not new.username:
...     new.username = 'New User'
...
>>> new.address.geo.lat = "-42.3433"
>>> new.address.geo.lng = "74.3433"
>>> new.email = 'someone@somewhere.biz'
>>> print new.pretty_print()
{
    "username": "New User",
    "email": "someone@somewhere.biz",
    "id": 5,
    "address": {
        "geo": {
            "lat": "-42.3433",
            "lng": "74.3433"
        }
    }
}
```
### Callables
Callable properties will be encoded via [cloudpickle](https://github.com/cloudpipe/cloudpickle) and base64 prefixed with `__callable__: `.
```python
>>> import RestResponse
>>> data = RestResponse.parse({'callable': lambda x: x + 1})
>>> data.callable
<function <lambda> at 0x7f92593de9b0>
>>> data.callable(1)
2
>>> pretty_str = data.pretty_print()
>>> print pretty_str
{
    "callable": "__callable__: gAJjY2xvdWRwaWNrbGUuY2xvdWRwaWNrbGUKX2ZpbGxfZnVuY3Rpb24KcQAoY2Nsb3VkcGlja2xlLmNsb3VkcGlja2xlCl9tYWtlX3NrZWxfZnVuYwpxAWNjbG91ZHBpY2tsZS5jbG91ZHBpY2tsZQpfYnVpbHRpbl90eXBlCnECVQhDb2RlVHlwZXEDhXEEUnEFKEsBSwFLAktDVQh8AABkAQAXU3EGTksBhnEHKVUBeHEIhXEJVQc8c3RkaW4+cQpVCDxsYW1iZGE+cQtLAVUAcQwpKXRxDVJxDkr/////VQhfX21haW5fX3EPh3EQUnERfXESKFUEbmFtZXETaAtVA2RvY3EUTlUGbW9kdWxlcRVoD1UOY2xvc3VyZV92YWx1ZXNxFk5VB2dsb2JhbHNxF31xGFUEZGljdHEZfXEaVQhkZWZhdWx0c3EbTnV0Ui4="
}
>>> data = RestResponse.loads(pretty_str)
>>> data.callable(1)
2
```
### Binary
Properties detected as binary data will be encoded via base64 prefixed with `__binary__: `.
```python
>>> import RestResponse
>>> import requests
>>> data = RestResponse.parse({
... 'binary': requests.get('https://cataas.com/cat').content
... })
>>> data.binary
'\xff\xd8\xff\xdb\x00C\x00\x06\x04\x05\x06\x05\x04\x06\x06\x05\x06\x07\x07\x06\x08\n\x10\n\n\t\t\n\x14\x0e\x0f\x0c\x10\x17\x14\x18\x18\x17\x14\x16\x16\x1a\x1d%\x1f\x1a\x1b#\x1c\x16\x16 , #&\')*)\x19\x1f-0-(0%()(\xff\xdb\x00C\x01\x07\x07\x07\n\x08\n\x13\n\n\x13(\x1a\x16\x1a((((((((((((((((((((((((((((((((((((((((((((((((((\xff\xc2\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\xff\xc4\x00\x14\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xda\x00\x0c\x03\x01\x00\x02\x10\x03\x10\x00\x00\x01\x90\x07\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x01\x05\x02\x7f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x03\x01\x01?\x01\x7f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x02\x01\x01?\x01\x7f\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x06?\x02\x7f\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x01?!\x7f\xff\xda\x00\x0c\x03\x01\x00\x02\x00\x03\x00\x00\x00\x10\xfb\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x03\x01\x01?\x10\x7f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x02\x01\x01?\x10\x7f\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x01?\x10\x7f\xff\xd9'
>>> pretty_str = data.pretty_print()
>>> print pretty_str
{
    "binary": "__binary__: /9j/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wgARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAT/xAAUAQEAAAAAAAAAAAAAAAAAAAAB/9oADAMBAAIQAxAAAAGQB//EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAQUCf//EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQMBAT8Bf//EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQIBAT8Bf//EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEABj8Cf//EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAT8hf//aAAwDAQACAAMAAAAQ+//EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQMBAT8Qf//EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQIBAT8Qf//EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAT8Qf//Z"
}
>>> data = RestResponse.loads(pretty_str)
>>> data.binary
'\xff\xd8\xff\xdb\x00C\x00\x06\x04\x05\x06\x05\x04\x06\x06\x05\x06\x07\x07\x06\x08\n\x10\n\n\t\t\n\x14\x0e\x0f\x0c\x10\x17\x14\x18\x18\x17\x14\x16\x16\x1a\x1d%\x1f\x1a\x1b#\x1c\x16\x16 , #&\')*)\x19\x1f-0-(0%()(\xff\xdb\x00C\x01\x07\x07\x07\n\x08\n\x13\n\n\x13(\x1a\x16\x1a((((((((((((((((((((((((((((((((((((((((((((((((((\xff\xc2\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\xff\xc4\x00\x14\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xda\x00\x0c\x03\x01\x00\x02\x10\x03\x10\x00\x00\x01\x90\x07\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x01\x05\x02\x7f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x03\x01\x01?\x01\x7f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x02\x01\x01?\x01\x7f\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x06?\x02\x7f\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x01?!\x7f\xff\xda\x00\x0c\x03\x01\x00\x02\x00\x03\x00\x00\x00\x10\xfb\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x03\x01\x01?\x10\x7f\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x02\x01\x01?\x10\x7f\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x01?\x10\x7f\xff\xd9'
```
### NoneProp
It should be noted that missing referenced properties, including nested, are gracefully falsey.

```python
>>> import RestResponse
>>> data = RestResponse.parse({})
>>> data.property.is_none
None
>>> bool(data.property.is_none)
False
>>> isinstance(data.property.is_none, RestResponse.NoneProp)
True
>>> 'some data' in data.property.is_none
False
>>> [x for x in data.property.is_none]
[]
>>> data.property.is_none = None
>>> isinstance(data.property.is_none, RestResponse.NoneProp)
False
>>> print data.pretty_print()
{
    "property": {
        "is_none": null
    }
}
```
### SQLAlchemy ORM
RestResponse uses a Mutable mixin provided by SQLAlchemy for interfacing with databases. The following (Flask) snippet should get you started:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from RestResponse.orm.sqlalchemy import RESTResponse


app = Flask(__name__)
db = SQLAlchemy(app)


class SomeModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    data = db.Column(RESTResponse(), nullable=False)

    def __init__(self, data):
        self.data = data # data should be json serializable
```
Data will be saved to the database as a serialized json blob. When data is loaded it will be coerced to the underlying RestResponseObj

## ApiModel

Inherit RestResponse.ApiModel to facilitate typing out API models. Please note your properties should NOT start with `_`. `ApiModel._data` setter ensures that passed in data conforms to your properties, effectively filtering out underscored properties identified via `dir()`. Consider the following snippet:
```python
from RestResponse import ApiModel, ApiCollection


class Model(ApiModel):
    def __init__(self, data):
        self._data = data

    # this _foo property will be ignored on init
    @property
    def _foo(self):
        return str(self._data._foo) if self._data._foo

    @_foo.setter
    def _foo(self, _foo):
        self._data._foo = str(_foo)

    @property
    def id(self):
        return int(self._data.id) if self._data.id else None

    @id.setter
    def id(self, id):
        self._data.id = int(id)

    @property
    def reference(self):
        if not self._data.reference:
            self._data.reference = Reference()
        return Reference(self._data.reference)

    @reference.setter
    def reference(self, reference):
        self._data.reference = Reference(reference)

    @property
    def int_collection(self):
        if not self._data.int_collection:
            self._data.int_collection = ApiCollection(int)
        return self._data.int_collection

    @int_collection.setter
    def int_collection(self, int_collection):
        if not self._data.int_collection:
            self._data.int_collection = ApiCollection(int)
        self._data.int_collection.extend([int(x) for x in int_collection])

    @property
    def ref_collection(self):
        if not self._data.ref_collection:
            self._data.ref_collection = ApiCollection(Reference)
        return self._data.ref_collection

    @ref_collection.setter
    def ref_collection(self, ref_collection):
        if not self._data.ref_collection:
            self._data.ref_collection = ApiCollection(Reference)
        self._data.ref_collection.extend([Reference(x) for x in ref_collection])


class Reference(ApiModel):
    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return int(self._data.id) if self._data.id else None

    @id.setter
    def id(self, id):
        self._data.id = int(id)
```
Then initialize with RestObject, dict, ApiModel, or serialized JSON
```python
>>> model = Model({
    'id': 5,
    'ref': {
        'id': 5,
        'foo': 'bar'
    },
    'int_collection': [1, 2, 3],
    'ref_collection': [
        {
            'id': 1,
        },
        {
            'id': 2,
        }
    ],
    'foo': 'bar',
    '_foo': '_bar'
})
>>> print model._data.pretty_print()
{
    "int_collection": [
        1,
        2,
        3
    ],
    "ref": {
        "id": 5
    },
    "ref_collection": [
        {
            "id": 1
        },
        {
            "id": 2
        }
    ],
    "id": 5
}
>>> assert '_foo' not in model._data
>>> assert 'foo' not in model._data
>>> assert 'foo' not in model.ref._data
>>> type(model._data)
<class 'RestResponse.objects.RestObject'>
```
Note: ApiModel will NOT decode/encode binary/callable types by default. You'll need to turn this behavior on by overriding `ApiModel.__opts__`:
```python
Model.__opts__ = {
    'encode_binary': True,
    'encode_callable': True,
    'decode_binary': True,
    'decode_callable': True
}
```

## Testing

    $ pytest -s tests/tests.py

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/tysonholub/RestResponse.git. This project is
intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the
[Contributor Covenant](http://contributor-covenant.org) code of conduct.


## License

This package is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
