from sqlalchemy import types
import json
from RestResponse import RestResponse, RestResponseObj, RestEncoder


class RestResponseEncodedObj(types.TypeDecorator):
    impl = types.LargeBinary

    def process_bind_param(self, value, dialect):
        if value is not None:
            result = json.dumps(value, cls=RestEncoder)
            if isinstance(result, str):
                result = result.encode('utf-8')
            return result

    def process_result_value(self, value, dialect):
        if value:
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            return RestResponse.loads(value)
        else:
            return RestResponse.parse({})


def RESTResponse():
    return RestResponseObj.as_mutable(RestResponseEncodedObj())
