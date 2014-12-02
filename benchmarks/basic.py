
import time, os
try:
    from jitpy import setup
    import numba
    CPYTHON = True
except:
    CPYTHON = False
else:
    setup(os.environ['PYPY_HOME'])
    from jitpy.wrapper import jittify

NUMBER = 1000000

def f(a, b, c):
    return 1

def f2(a, b, c):
    s = 0
    for i in xrange(a):
        s += a
        s += b
        s += c
    return s

def check_py(f):
    for i in xrange(NUMBER):
        f(10, i, i)

def check_jitpy(f):
    jit_f = jittify([int, int, int], int)(f)
    for i in xrange(NUMBER):
        jit_f(10, i, i)

def check_numba(f):
    jit_f = numba.jit(f)
    for i in xrange(NUMBER):
        jit_f(10, i, i)

if CPYTHON:
    ALL = [('PY', check_py), ('JITPY', check_jitpy), ('NUMBA', check_numba)]
else:
    ALL = [('PY', check_py)]

for bench_name, bench_func in [('basic', f), ('basic_loop', f2)]:
    print bench_name
    for name, func in ALL:
        t0 = time.time()
        func(bench_func)
        print name, time.time() - t0
