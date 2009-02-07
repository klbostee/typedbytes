import cPickle
import types
from struct import pack, unpack


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

MARKER = 255


class Input(object):

    def __init__(self, file):
        self.file = file

    def read(self):
        t = self.read_type()
        if t == None:
            return None
        elif t == BYTE:
            return self.read_byte()
        elif t == BOOL:
            return self.read_bool()
        elif t == INT:
            return self.read_int()
        elif t == LONG:
            return self.read_long()
        elif t == FLOAT:
            return self.read_float()
        elif t == DOUBLE:
            return self.read_double()
        elif t == STRING:
            return self.read_string()
        elif t == VECTOR:
            return self.read_vector()
        elif t == LIST:
            return self.read_list()
        elif t == MAP:
            return self.read_map()
        elif t == BYTES:
            bytes = self.read_bytes()
            try:
                return cPickle.loads(bytes)
            except cPickle.UnpicklingError:
                return bytes
        elif t == MARKER:
            return None
        else:
            raise ValueError("invalid type byte: " + str(t))

    def reads(self):
        record = self.read()
        while record != None:
            yield record
            record = self.read()

    def __iter__(self):
        return self.reads()

    def read_type(self):
        byte = self.file.read(1)
        if byte:
            return unpack('!B', byte)[0]

    def read_bytes(self):
        count = unpack('!i', self.file.read(4))[0]
        return self.file.read(count)
 
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
        return self.file.read(count)

    def read_vector(self):
        count = unpack('!i', self.file.read(4))[0]
        return tuple(Input.read(self) for i in xrange(count))

    def read_list(self):
        obj = Input.read(self)
        list_ = []
        while obj != None:
            list_.append(obj)
            obj = Input.read(self)
        return list_

    def read_map(self):
        count = unpack('!i', self.file.read(4))[0]
        return dict((Input.read(self), Input.read(self)) \
                    for i in xrange(count))


class Output(object):

    def __init__(self, file):
        self.file = file

    def __del__(self):
        if not file.closed:
            self.file.flush()

    def write(self, obj):
        t = type(obj)
        if t == types.BooleanType:
            self.write_bool(obj)
        elif t == types.IntType:
            # Python ints are 64 bit
            if -2147483648 <= obj <= 2147483647:
                self.write_int(obj)
            else:
                self.write_long(obj)
        elif t == types.FloatType:
            # Python floats are 64 bit
            if 1.40129846432481707e-45 <= obj <= 3.40282346638528860e+38:
                self.write_float(obj)
            else:
                self.write_double(obj)
        elif t == types.StringType:
            self.write_string(obj)
        elif t == types.TupleType:
            self.write_vector(obj)
        elif t == types.ListType:
            self.write_list(obj)
        elif t == types.DictType:
            self.write_map(obj)
        else:
            self.write_bytes(cPickle.dumps(obj, protocol=2))

    def writes(self, iterable):
        for obj in iter(iterable):
            self.write(obj)

    def write_bytes(self, bytes):
        self.file.write(pack('!Bi', BYTES, len(bytes)))
        self.file.write(bytes)

    def write_byte(self, byte):
        self.file.write(pack('!Bb', BYTE, byte))

    def write_bool(self, bool_):
        self.file.write(pack('!Bb', BOOL, int(bool_)))

    def write_int(self, int_):
        self.file.write(pack('!Bi', INT, int_))

    def write_long(self, long_):
        self.file.write(pack('!Bq', LONG, long_)) 

    def write_float(self, float_):
        self.file.write(pack('!Bf', FLOAT, float_))

    def write_double(self, double):
        self.file.write(pack('!Bd', DOUBLE, double))

    def write_string(self, string):
        self.file.write(pack('!Bi', STRING, len(string)))
        self.file.write(string)

    def write_vector(self, vector):
        self.file.write(pack('!Bi', VECTOR, len(vector)))
        for obj in vector:
            Output.write(self, obj)

    def write_list(self, list_):
        self.file.write(pack('!B', LIST))
        for obj in list_:
            Output.write(self, obj)
        self.file.write(pack('!B', MARKER))

    def write_map(self, map):
        self.file.write(pack('!Bi', MAP, len(map)))
        for (key, value) in map.iteritems():
            Output.write(self, key)
            Output.write(self, value)


class PairedInput(Input):

    def read(self):
        record = Input.read(self)
        if record != None:
            return (record, Input.read(self))


class PairedOutput(Output):

    def write(self, pair):
        Output.write(self, pair[0])
        Output.write(self, pair[1])


def findmodpath():
    import os, sys
    process = os.popen(sys.executable + ' -m typedbytes modpath')
    modpath = process.readlines()[0].strip()   
    process.close()
    return modpath


if __name__ == "__main__":
    import sys
    print sys.argv[0]
