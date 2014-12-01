
import inspect
from jitpy import ffi, ptr
from jitpy.exc import JitPyException

converters = {
    int: 'long',
    float: 'double',
    str: 'char*',
    None: 'void',
    'array': 'intptr_t*',
}

def jittify(argtypes, restype):
    """ Wrap function into a callable visible from CPython, but run on
    underlaying PyPy.
    """
    if not ptr:
        raise Exception("jitpy not initialized, call jitpy.setup(pypy_home)")
    ll_tp = converters[restype] + ' (*)(' + ', '.join(
        [converters[arg] for arg in argtypes]) + ')'
    ll_arrays = []
    for arg in argtypes:
        if arg == 'array':
            ll_arrays.append('a')
        else:
            ll_arrays.append(' ')
    ll_arrays = ''.join(ll_arrays)

    def convert(ll_tp, arg):
        if ll_tp == 'array':
            assert arg.dtype == int # for now
            return ffi.cast("void *", id(arg))
        return arg
    
    def decorator(fn):
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
        def func(*args):
            args = [convert(argtypes[i], args[i]) for i in range(len(args))]
            res = ll_handle(*args)
            if not res and ptr.last_exception:
                exception_repr = ffi.string(ptr.last_exception)
                ptr.last_exception = ffi.NULL
                raise JitPyException(exception_repr)
            return res
        return func
    return decorator

def clean_namespace():
    if not ptr:
        raise Exception("jitpy not initialized, call jitpy.setup(pypy_home)")
    ptr.clean_namespace()
