
import inspect
import py
from jitpy import ffi, ptr
from jitpy.exc import JitPyException

converters = {
    int: 'long',
    float: 'double',
    str: 'char*',
    None: 'void',
    'array': 'intptr_t*',
}

def jittify(argtypes, restype=None):
    """ Wrap function into a callable visible from CPython, but run on
    underlaying PyPy.
    """
    if not ptr:
        raise Exception("jitpy not initialized, call jitpy.setup(pypy_home)")
    ll_tp = converters[restype] + ' (*)(' + ', '.join(
        [converters[arg] for arg in argtypes]) + ')'
    if restype == 'array':
        raise TypeError("Cannot use arrays as a return type yet")
    ll_arrays = []
    for arg in argtypes:
        if arg == 'array':
            ll_arrays.append('a')
        else:
            ll_arrays.append(' ')
    ll_arrays = ''.join(ll_arrays)

    def decorator(fn):
        def convert_numpy_array(ll_tp, arg):
            return ffi.cast("void *", id(arg))
    
        lines = inspect.getsource(fn).splitlines()
        for i, line in enumerate(lines):
            if line.strip(' ').startswith('@'):
                continue
            lines[i] = line.strip(' ')
            break
        source = "\n".join(lines[i:])
        name = fn.__name__
        handle = ptr.basic_register(source, name, ll_tp, ll_arrays)
        if not handle:
            raise Exception("basic_register failed")
        ll_handle = ffi.cast(ll_tp, handle)
        argspec = ", ".join(["arg%d" % i for i in range(len(argtypes))])
        conversions = []
        for i, arg in enumerate(argtypes):
            if arg == 'array':
                conversions.append("    arg%d = ffi.cast('void *', id(arg%d))"
                                   % (i, i))
        conversions = "\n".join(conversions)
        source = py.code.Source("""
        def func(%(args)s):
        %(conversions)s
            res = ll_handle(%(args)s)
            if not res and ptr.last_exception:
                exception_repr = ffi.string(ptr.last_exception)
                ptr.last_exception = ffi.NULL
                raise JitPyException(exception_repr)
            return res
        """ % {"args": argspec, 'conversions': conversions})
        namespace = {'ffi': ffi, 'll_handle': ll_handle,
                     'JitPyException':JitPyException, 'ptr': ptr}
        exec source.compile() in namespace
        res = namespace['func']
        res.__name__ = fn.__name__
        return res
    return decorator

def clean_namespace():
    if not ptr:
        raise Exception("jitpy not initialized, call jitpy.setup(pypy_home)")
    ptr.clean_namespace()
