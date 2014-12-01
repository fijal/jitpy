
import os
from jitpy.wrapper import setup
if 'PYPY_HOME' not in os.environ:
    raise Exception("please setup PYPY_HOME to point to your pypy installation")
setup(os.environ['PYPY_HOME'])
from jitpy.wrapper import jittify

class TestJitPy(object):
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
