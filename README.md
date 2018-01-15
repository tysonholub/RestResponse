# RestResponse

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

Import RestResponse and call parse on any list, dict, or primitive

```python
>>> import RestResponse
>>> import requests
>>> r = requests.get('http://jsonplaceholder.typicode.com/users')
>>> users = RestResponse.parse(r.json())
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

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/MobiusWorksLLC/RestResponse.git. This project is
intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the
[Contributor Covenant](http://contributor-covenant.org) code of conduct.


## License

The gem is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
