
import cffi, new, os, traceback, sys
from _numpypy import multiarray as numpy

ffi = cffi.FFI()
ffi.cdef(open(os.path.join(cur_dir, "pypy.defs")).read())

MAX_FUNCTIONS = 100
all_callbacks = []

mod = new.module('__global__')
last_exception = None

if sys.maxint == (1 << 31) - 1:
    WORD = 4
else:
    WORD = 8

# XXX copy
numpy_types = {
    0: 'b',
    1: 'i1',
    2: 'u1',
    3: 'i2',
    4: 'u2',
    5: 'int',
    6: 'uint',
    7: 'int',
    8: 'uint',
    9: 'longlong',
    10: 'ulonglong',
    11: 'single',
    12: 'double',
    13: 'longdouble',
    14: 'csingle',
    15: 'cdouble',
    16: 'clongdouble',
    #17: 'object',
    # rest not supported
}

def convert_from_numpy_array(ll_a):
    data = (ll_a + NumpyData.data_offset)[0]
    strides = ffi.cast("intptr_t*", (ll_a + NumpyData.strides_offset)[0])
    dims = ffi.cast("intptr_t*", (ll_a + NumpyData.dimensions_offset)[0])
    nd = ffi.cast('int *', (ll_a + NumpyData.nd_offset))[0]
    dims = [dims[i] for i in range(nd)]
    strides = [strides[i] for i in range(nd)]
    data = ffi.buffer(ffi.cast("char*", data), sys.maxint)
    # XXX strides
    descr = ffi.cast('char*', (ll_a + NumpyData.descr_offset)[0])
    type_num = ffi.cast('int*', descr + NumpyData.type_num_offset)[0]
    dtype = numpy_types[type_num]
    return numpy.ndarray(dims, buffer=data, dtype=dtype)

def wrap_exception_and_arrays(func, arrays):
    args = ', '.join(['arg%d' % i for i in range(len(arrays))])
    conversions = []
    for i, arg in enumerate(arrays):
        if arg == 'a':
            conversions.append('        arg%d = convert_from_numpy_array(arg%d)'
                               % (i, i))
    conversions = '\n'.join(conversions)
    source = """def wrapper(%(args)s):
    global last_exception

    try:
%(conversions)s
        return func(%(args)s)
    except Exception, e:
        tb_repr = (''.join(traceback.format_tb(sys.exc_info()[2])) +
                   '%%s:%%s' %% (e.__class__.__name__, e))
        last_exception = ffi.new('char[]', tb_repr)
        pypy_def.last_exception = last_exception
    return 0
    """ % {'args': args, 'conversions': conversions}
    namespace = {'traceback': traceback, 'ffi': ffi, 'pypy_def': pypy_def,
                 'func': func, 'sys': sys,
                 'convert_from_numpy_array': convert_from_numpy_array}
    exec source in namespace
    return namespace['wrapper']

@ffi.callback("void* (*)(char *, char *, char *, char *)")
def basic_register(ll_source, ll_name, ll_tp, ll_arrays):
    source = ffi.string(ll_source)
    name = ffi.string(ll_name)
    tp = ffi.string(ll_tp)
    exec source in mod.__dict__
    func = wrap_exception_and_arrays(mod.__dict__[name],
                                     ffi.string(ll_arrays), )
    ll_callback = ffi.callback(tp)(func)
    all_callbacks.append(ll_callback)
    return ffi.cast('void *', ll_callback)

@ffi.callback("void (*)()")
def clean_namespace():
    mod.__dict__.clear()

@ffi.callback("void (*)(char *)")
def extra_source(ll_source):
    source = ffi.string(ll_source)
    exec source in mod.__dict__

class NumpyData(object):
    pass

@ffi.callback("void (*)(int*)")
def setup_numpy_data(offsets):
    NumpyData.data_offset = offsets[0] / WORD
    NumpyData.strides_offset = offsets[1] / WORD
    NumpyData.dimensions_offset = offsets[2] / WORD
    NumpyData.nd_offset = offsets[3] / WORD
    NumpyData.descr_offset = offsets[4] / WORD
    NumpyData.type_num_offset = offsets[5]

pypy_def = ffi.cast("struct pypy_defs*", c_argument)
pypy_def.basic_register = basic_register
pypy_def.clean_namespace = clean_namespace
pypy_def.extra_source = extra_source
pypy_def.setup_numpy_data = setup_numpy_data
