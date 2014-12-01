
import os, py
from jitpy import setup, extra_source
from jitpy.exc import JitPyException
if 'PYPY_HOME' not in os.environ:
    raise Exception("please setup PYPY_HOME to point to your pypy installation")
setup(os.environ['PYPY_HOME'])
from jitpy.wrapper import jittify, clean_namespace

class TestJitPy(object):
    def setup_method(self, meth):
        clean_namespace()
    
    def test_float_func(self):
        @jittify([float, float], float)
        def func(a, b):
            return a + b

        assert func(1.2, 2.4) == 1.2 + 2.4

    def test_int_func(self):
        @jittify([int, int], int)
        def func(a, b):
            return a + b

        assert func(2, 4) == 6

    def test_cross_reference(self):
        extra_source("""class X:
        def __init__(self, x):
            self.x = x
        """)

        @jittify([], int)
        def func():
            return X(42).x

        assert func() == 42

    def test_exception_wrapping(self):
        @jittify([], int)
        def func():
            raise Exception("foo")

        e = py.test.raises(JitPyException, func)
        assert 'Exception:foo' in str(e.value)
