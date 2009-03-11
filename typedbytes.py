def classes():

    from cPickle import dumps, loads, UnpicklingError, HIGHEST_PROTOCOL
    from struct import pack, unpack, error as StructError

    BYTES = 0
    BYTE = 1
    BOOL = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    STRING = 7
    VECTOR = 8
    LIST = 9
    MAP = 10
    PICKLE = 100
    MARKER = 255
    LIST_CODE, MARKER_CODE = (pack('!B', i) for i in (LIST, MARKER))
    STRING_ENCODING = 'utf8'

    _len = len

    class Input(object):

        def __init__(self, file):
            self.file = file
            self.eof = False

        def _read(self):
            try:
                t = unpack('!B', self.file.read(1))[0]
            except StructError:
                self.eof = True
                raise StopIteration
            # A guess at frequency order:
            if   t == INT:
                return self.read_int()
            elif t == LONG:
                return self.read_long()
            elif t == STRING:
                return self.read_string()
            elif t == BYTES:
                bytes = self.read_bytes()
            elif t == VECTOR:
                return self.read_vector()
            elif t == LIST:
                return self.read_list()
            elif t == MAP:
                return self.read_map()
            elif t == BOOL:
                return self.read_bool()
            elif t == DOUBLE:
                return self.read_double()
            elif t == MARKER:
                raise StopIteration
            elif t == FLOAT:
                return self.read_float()
            elif t == BYTE:
                return self.read_byte()
            elif t == PICKLE:
                return self.read_pickle()
            else:
                raise StructError("Invalid type byte: " + str(t))

        def read(self):
            try:
                return self._read()
            except StopIteration:
                return None

        def _reads(self):
            r = self._read
            while 1:
                yield r()

        __iter__ = reads = _reads

        def close(self):
            self.file.close()

        def read_bytes(self):
            count = unpack('!i', self.file.read(4))[0]
            value = self.file.read(count)
            if _len(value) != count:
                raise StructError("EOF before reading all of bytes type")
            return value

        def read_byte(self):
            return unpack('!b', self.file.read(1))[0]

        def read_bool(self):
            return bool(unpack('!b', self.file.read(1))[0])

        def read_int(self):
            return unpack('!i', self.file.read(4))[0]

        def read_long(self):
            return unpack('!q', self.file.read(8))[0]

        def read_float(self):
            return unpack('!f', self.file.read(4))[0]

        def read_double(self):
            return unpack('!d', self.file.read(8))[0]

        def read_string(self):
            count = unpack('!i', self.file.read(4))[0]
            value = self.file.read(count)
            if _len(value) != count:
                raise StructError("EOF before reading all of String")
            return value.decode(STRING_ENCODING)

        def read_vector(self):
            r = self._read
            count = unpack('!i', self.file.read(4))[0]
            try:
                return tuple(r() for i in xrange(count))
            except StopIteration:
                raise StructError("EOF before all vector elements read")

        def read_list(self):
            value = list(self._reads())
            if self.eof:
                raise StructError("EOF before end-of-list marker")
            return value

        def read_map(self):
            r = self._read
            count = unpack('!i', self.file.read(4))[0]
            return dict((r(), r()) for i in xrange(count))

        def read_pickle(self):
            count = unpack('!i', self.file.read(4))[0]
            bytes = self.file.read(count)
            if _len(bytes) != count:
                raise StructError("EOF before reading all of bytes type")
            return loads(bytes)


    _isinstance, _int, _long, _unicode = isinstance, int, long, unicode
    _bool, _float, _tuple, _list, _dict = bool, float, tuple, list, dict


    def flatten(iterable):
        for i in iterable:
            for j in i:
                yield j


    class Output(object):

        def __init__(self, file):
            self.file = file

        def __del__(self):
            if not file.closed:
                self.file.flush()

        def _write(self, obj):
            # A guess at frequency order:
            if _isinstance(obj, (_int, _long)):
                if -2147483648 <= obj <= 2147483647:
                    self.write_int(obj)
                elif -9223372036854775808L <= obj <= 9223372036854775807L:
                    self.write_long(obj)
                else:
                    self.write_pickle(obj)
            elif _isinstance(obj, _unicode):
                self.write_string(obj)
            elif _isinstance(obj, _bool):
                self.write_bool(obj)
            elif _isinstance(obj, _float):
                self.write_double(obj) # Python floats are 64-bit
            elif _isinstance(obj, _tuple):
                self.write_vector(obj)
            elif _isinstance(obj, _list):
                self.write_list(obj)
            elif _isinstance(obj, _dict):
                self.write_map(obj)
            else:
                self.write_pickle(obj)

        write = _write

        def _writes(self, iterable):
            w = self._write
            for obj in iterable:
                w(obj)

        writes = _writes

        def flush(self):
            self.file.flush()

        def close(self):
            self.file.close()

        def write_bytes(self, bytes):
            self.file.write(pack('!Bi', BYTES, _len(bytes)))
            self.file.write(bytes)

        def write_byte(self, byte):
            self.file.write(pack('!Bb', BYTE, byte))

        def write_bool(self, bool_):
            self.file.write(pack('!Bb', BOOL, _int(bool_)))

        def write_int(self, int_):
            self.file.write(pack('!Bi', INT, int_))

        def write_long(self, long_):
            self.file.write(pack('!Bq', LONG, long_)) 

        def write_float(self, float_):
            self.file.write(pack('!Bf', FLOAT, float_))

        def write_double(self, double):
            self.file.write(pack('!Bd', DOUBLE, double))

        def write_string(self, string):
            string = string.encode(STRING_ENCODING)
            self.file.write(pack('!Bi', STRING, _len(string)))
            self.file.write(string)

        def write_vector(self, vector):
            self.file.write(pack('!Bi', VECTOR, _len(vector)))
            self._writes(vector)

        def write_list(self, list_):
            self.file.write(LIST_CODE)
            self._writes(list_)
            self.file.write(MARKER_CODE)

        def write_map(self, map):
            self.file.write(pack('!Bi', MAP, _len(map)))
            self._writes(flatten(map.iteritems()))

        def write_pickle(self, obj):
            bytes = dumps(obj, HIGHEST_PROTOCOL)
            self.file.write(pack('!Bi', PICKLE, _len(bytes)))
            self.file.write(bytes)


    class PairedInput(Input):

        def read(self):
            try:
                key = self._read()
            except StopIteration:
                return None
            try:
                value = self._read()
            except StopIteration:
                raise StructError('EOF before second item in pair')
            return key, value

        def reads(self):
            it = self._reads()
            next = it.next
            while 1:
                key = next()
                try:
                    value = next()
                except StopIteration:
                    raise StructError('EOF before second item in pair')
                yield key, value

        __iter__ = reads


    class PairedOutput(Output):

        def write(self, pair):
            self._writes(pair)

        def writes(self, iterable):
            self._writes(flatten(iterable))


    return Input, Output, PairedInput, PairedOutput


Input, Output, PairedInput, PairedOutput = classes()
