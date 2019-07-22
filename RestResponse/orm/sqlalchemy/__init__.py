from sqlalchemy import types
import json
from RestResponse import RestResponse, RestResponseObj, RestEncoder, utils


class RestResponseEncodedObj(types.TypeDecorator):
    impl = types.Binary

    def process_bind_param(self, value, dialect):
        if value:
            result = json.dumps(value, cls=RestEncoder)
            if utils.PYTHON3 and isinstance(result, str):
                result = result.encode('utf-8')
            return result

    def process_result_value(self, value, dialect):
        if value:
            if utils.PYTHON3 and isinstance(value, bytes):
                value = value.decode('utf-8')
            return RestResponse.loads(value)
        else:
            return RestResponse.parse(None)


def RESTResponse():
    return RestResponseObj.as_mutable(RestResponseEncodedObj())
