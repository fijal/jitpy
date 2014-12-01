
import cffi, new, os
ffi = cffi.FFI()
ffi.cdef(open(os.path.join(cur_dir, "pypy.defs")).read())

MAX_FUNCTIONS = 100
all_callbacks = []

mod = new.module('__global__')

@ffi.callback("void* (*)(char *, char *, char *)")
def basic_register(ll_source, ll_name, ll_tp):
    source = ffi.string(ll_source)
    name = ffi.string(ll_name)
    tp = ffi.string(ll_tp)
    exec source in mod.__dict__
    func = mod.__dict__[name]
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

pypy_def = ffi.cast("struct pypy_defs*", c_argument)
pypy_def.basic_register = basic_register
pypy_def.clean_namespace = clean_namespace
pypy_def.extra_source = extra_source
