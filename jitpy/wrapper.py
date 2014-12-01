
import inspect
from jitpy import ffi, ptr

converters = {
    int: 'long',
    float: 'double',
    str: 'char*',
}

def jittify(argtypes, restype):
    """ Wrap function into a callable visible from CPython, but run on
    underlaying PyPy.
    """
    if not ptr:
        raise Exception("jitpy not initialized, call jitpy.setup(pypy_home)")
    ll_tp = converters[restype] + ' (*)(' + ', '.join(
        [converters[arg] for arg in argtypes]) + ')'
    def decorator(fn):
        lines = inspect.getsource(fn).splitlines()
        for i, line in enumerate(lines):
            if line.strip(' ').startswith('@'):
                continue
            lines[i] = line.strip(' ')
            break
        source = "\n".join(lines[i:])
        name = fn.__name__
        handle = ptr.basic_register(source, name, ll_tp)
        if not handle:
            raise Exception("basic_register failed")
        return ffi.cast(ll_tp, handle)
    return decorator

def clean_namespace():
    if not ptr:
        raise Exception("jitpy not initialized, call jitpy.setup(pypy_home)")
    ptr.clean_namespace()
