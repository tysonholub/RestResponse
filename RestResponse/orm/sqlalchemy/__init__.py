from sqlalchemy import types
import json
from RestResponse import RestResponse, RestResponseObj


class RestResponseEncodedObj(types.TypeDecorator):
    impl = types.Binary

    def process_bind_param(self, value, dialect):
        if value:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value:
            return RestResponse.parse(json.loads(value))
        else:
            return RestResponse.parse(None)


def RESTResponse():
    return RestResponseObj.as_mutable(RestResponseEncodedObj())
