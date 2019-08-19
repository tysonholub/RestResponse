from RestResponse import ApiModel, ApiCollection


class Model(ApiModel):
    def __init__(self, data):
        self._data = data

    @property
    def _foo(self):
        return self._get_string(self._data._foo)

    @_foo.setter
    def _foo(self, _foo):
        self._data._foo = self._set_string(_foo)

    @property
    def id(self):
        return self._get_int(self._data.id)

    @id.setter
    def id(self, id):
        self._data.id = self._set_int(id)

    @property
    def id_doesnt_raise(self):
        return self._get_int(self._data.id_doesnt_raise)

    @id_doesnt_raise.setter
    def id_doesnt_raise(self, id):
        self._data.id_doesnt_raise = self._format_int(id, raises_value_error=False)

    @property
    def string(self):
        return self._get_string(self._data.string)

    @string.setter
    def string(self, string):
        self._data.string = self._set_string(string)

    @property
    def string_doesnt_raise(self):
        return self._get_string(self._data.string_doesnt_raise)

    @string_doesnt_raise.setter
    def string_doesnt_raise(self, string):
        self._data.string_doesnt_raise = self._format_string(string, raises_value_error=False)

    @property
    def floating_point(self):
        return self._get_float(self._data.floating_point)

    @floating_point.setter
    def floating_point(self, floating_point):
        self._data.floating_point = self._set_float(floating_point)

    @property
    def floating_point_doesnt_raise(self):
        return self._get_float(self._data.floating_point_doesnt_raise)

    @floating_point_doesnt_raise.setter
    def floating_point_doesnt_raise(self, floating_point):
        self._data.floating_point_doesnt_raise = self._format_float(floating_point, raises_value_error=False)

    @property
    def date_time(self):
        return self._get_datetime(self._data.date_time)

    @date_time.setter
    def date_time(self, date_time):
        self._data.date_time = self._set_datetime(date_time)

    @property
    def date_time_doesnt_raise(self):
        return self._get_datetime(self._data.date_time_doesnt_raise)

    @date_time_doesnt_raise.setter
    def date_time_doesnt_raise(self, date_time):
        self._data.date_time_doesnt_raise = self._format_datetime(date_time, raises_value_error=False)

    @property
    def date(self):
        return self._get_date(self._data.date)

    @date.setter
    def date(self, date):
        self._data.date = self._set_date(date)

    @property
    def date_doesnt_raise(self):
        return self._get_date(self._data.date_doesnt_raise)

    @date_doesnt_raise.setter
    def date_doesnt_raise(self, date):
        self._data.date_doesnt_raise = self._format_date(date, raises_value_error=False)

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
    def ref(self):
        if not self._data.ref:
            self._data.ref = Ref()
        return Ref(self._data.ref)

    @ref.setter
    def ref(self, ref):
        self._data.ref = Ref(ref)

    @property
    def ref_collection(self):
        if not self._data.ref_collection:
            self._data.ref_collection = ApiCollection(Ref)
        return self._data.ref_collection

    @ref_collection.setter
    def ref_collection(self, ref_collection):
        if not self._data.ref_collection:
            self._data.ref_collection = ApiCollection(Ref)
        self._data.ref_collection.extend([Ref(x) for x in ref_collection])


class Ref(ApiModel):
    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return self._get_int(self._data.id)

    @id.setter
    def id(self, id):
        self._data.id = self._set_int(id)

    @property
    def string(self):
        return self._get_string(self._data.string)

    @string.setter
    def string(self, string):
        self._data.string = self._set_string(string)


class OverridesModel(ApiModel):
    def __init__(self, data):
        self.__opts__['_overrides'] = ['_foo']
        self._data = data

    @property
    def _foo(self):
        return self._get_string(self._data._foo)

    @_foo.setter
    def _foo(self, _foo):
        self._data._foo = self._set_string(_foo)
