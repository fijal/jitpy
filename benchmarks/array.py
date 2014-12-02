
import time, os
from jitpy import setup, extra_source
setup(os.environ['PYPY_HOME'])
from jitpy.wrapper import jittify
import numba, numpy

ARRAY_SIZE = 10000
NUMBER = 1000

def f(a, s):
    for k in range(10):
        for i in xrange(a.shape[0]):
            s += a[i]
    return s

def prepare_f():
    return numpy.arange(ARRAY_SIZE)

def f2(a, s):
    for k in range(10):
        for i in xrange(a.shape[0]):
            for j in xrange(a.shape[1]):
                s += a[i, j]
    return s

def prepare_f2():
    return numpy.arange(ARRAY_SIZE).reshape(100, 100)

def f3(a, s):
    for k in range(10):
        for i in xrange(a.shape[0] - 1):
            for j in xrange(a.shape[1]):
                s += len((a[i, j], a[i + 1, j]))
    return s

def prepare_f3():
    return numpy.arange(ARRAY_SIZE).reshape(100, 100)

def f4(a, s):
    for k in range(10):
        for i in xrange(a.shape[0] - 1):
            for j in xrange(a.shape[1]):
                s += X(a[i, j]).x
    return s

def prepare_f4():
    return numpy.arange(ARRAY_SIZE).reshape(100, 100)

def check_py(f, prepare):
    a = prepare()
    for i in xrange(NUMBER / 10):
        f(a, 3.5)
    

def check_jitpy(f, prepare):
    jit_f = jittify(['array', float], float)(f)
    a = prepare()
    for i in xrange(NUMBER):
        jit_f(a, 3.5)

def check_numba(f, prepare):
    jit_f = numba.jit(f)
    a = prepare()
    for i in xrange(NUMBER):
        jit_f(a, 3.5)

class X(object):
    def __init__(self, x):
        self.x = x

extra_source("""
class X(object):
    def __init__(self, x):
        self.x = x    
""")

ALL = [('PY', check_py), ('JITPY', check_jitpy), ('NUMBA', check_numba)]
        
for bench_name, bench_func, prep_func in [
        ('array traversal', f, prepare_f),
        ('2d array traversal', f2, prepare_f2),
        ('tuple + array', f3, prepare_f3),
        ('instance creation', f4, prepare_f4)]:
    print bench_name
    for name, func in ALL:
        t0 = time.time()
        func(bench_func, prep_func)
        t = time.time() - t0
        if func is check_py:
            t *= 10
        print name, t
