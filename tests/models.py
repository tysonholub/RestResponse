from RestResponse import ApiModel, ApiCollection


class Model(ApiModel):
    def __init__(self, data):
        self._data = data

    @property
    def _foo(self):
        return str(self._data._foo) if self._data._foo else None

    @_foo.setter
    def _foo(self, _foo):
        self._data._foo = str(_foo)

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
