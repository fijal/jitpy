
import cffi, os, inspect, py

def setup(pypy_home):
    ffi = cffi.FFI()
    ffi.cdef("""
    void rpython_startup_code(void);

    long pypy_setup_home(char* home, int verbose);

    int pypy_execute_source(char* source);

    int pypy_execute_source_ptr(char* source, void* ptr);

    """)
    os.environ['LD_LIBRARY_PATH'] = os.path.join(pypy_home, 'bin')

    lib = ffi.verify("""
    #include <include/PyPy.h>
    """, libraries=["pypy-c"], include_dirs=[pypy_home], library_dirs=[os.path.join(pypy_home, 'bin')])
    curdir = os.path.dirname(os.path.abspath(__file__))
    defs = os.path.join(curdir, 'pypy.defs')
    ffi.cdef(open(defs).read())
    lib.rpython_startup_code()
    res = lib.pypy_setup_home(os.path.join(os.path.abspath(pypy_home), 'bin'),
                              1)
    pypy_side = os.path.join(curdir, 'pypy_side.py')
    if res == -1:
        raise Exception("cannot init pypy")
    ptr = ffi.new("struct pypy_defs*")
    res = lib.pypy_execute_source_ptr(str(py.code.Source("""
    import sys, traceback
    try:
        import os
        cur_dir = '%s'
        execfile('%s')
    except Exception, e:
        traceback.print_tb(sys.exc_info()[2])
        print "%%s:%%s" %% (e.__class__.__name__, e)
        raise
    """ % (curdir, pypy_side))), ptr)
    if res:
        raise Exception("error running pypy side")

    converters = {
        int: 'long',
        float: 'double',
        str: 'char*',
    }

    def jittify(argtypes, restype):
        """ Wrap function into a callable visible from CPython, but run on
        underlaying PyPy.
        """
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

    globals()['jittify'] = jittify
