.. jitpy documentation master file, created by
   sphinx-quickstart on Mon Dec  1 11:21:00 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to jitpy's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2

What it jitpy?
==============

jitpy is a hack to embed your PyPy inside your CPython, so you can
call pypy-optimized functions from cpython using limited interface,
provided the types you pass are either simple immutable types or numpy
arrays. It's similar in the use patters to `numba`_, however it does
have very different characteristics. A simple example

.. code-block:: python

  from jitpy import setup
  setup('<path-to-pypy-home>')
  from jitpy.wrapper import jittify

  @jittify([int, float], float)
  def func(count, no):
      s = 0
      for i in range(count):
         s += no
      return s

  func(100000, 1.2)

This function will perform computations in the underlaying PyPy, thus yielding
a significant speed benefit (around 50x in my case)

Motivation
==========

Installing
==========

jitpy requires a new PyPy (newer than 28th of Nov), which can be e.g.
downloaded from PyPy `nightlies`_. Otherwise it can be installed via
``pip install jitpy``.

Using jitpy
===========

jitpy is not magic - what it does it moves code across the boundary
between two different Python implementations. It means that while PyPy and
CPython don't share any data, you can pass ``ints``, ``floats``, ``strings``
and ``numpy arrays`` without copying, since it's done in-process. It's also
faster compared to out-of-process solutions. However, one needs to remember
that the namespaces are separate and all the functions and classes won't
be magically visible from the other side. The API looks like this:

* ``jitpy.setup(pypy_home)`` - has to be called before anything in order to
  point to the correct PyPy build directory. ``pypy_home`` points to the
  directory of pypy checkout/installation

* ``jitpy.wrapper.jittify(argtypes, restype=None)`` - a wrapper that's passed
  argument types as a list and restype as on of the:

  * ``int, float, string`` - immutable types. Additionally ``None`` can
    be used for return type

  * ``'array'`` - a numpy array, can only be used as an argument, not a return
    value. Also only simple types are supported for now (no compound dtypes,
    no string, unicode) or object dtypes

* ``jitpy.extra_source(source)`` - this will export the extra source visible
  from the other side. Example:

  .. code-block:: python

    jitpy.extra_source("""class X:
        def __init__(self, x):
            self.x = x
    """)

    class Y(object):
        pass

    @jitpy.wrapper.jittify([], int)
    def func():
        return X(42).x

    func()

  this will work, however trying to reference ``Y`` from inside the ``func``
  will result in ``NameError`` exception.

Any Python is allowed within the function, including imports, pdb, everything,
however ``sys.path`` is **not** inherited, so has to be set up separately within
the ``extra_source`` or some exported function definition.

Limitations
===========

The API is limited to builtin types, because it's easy to see how the boundary
looks like. Numpy arrays can be shared, because the data is visible as a pointer
in C on the low level. ``sys.path`` has to be initialized separately, but will
respect all the libraries installed in the underlaying ``pypy``.

Benchmarks
==========

Everyone loves benchmarks. The way one presents benchmarks is very important.
I'm going to compare on a limited set of benchmarks various tools designed
for a specific purpose -- speeding up Python in pieces or in whole without
learning a new language. That means that tools like Cython, C, Fortran are
out of scope of this comparison. I'm going to compare CPython, jitpy, numba
and to some extent PyPy.

The `basic benchmark`_ measures the overhead of calling through the layer.
The first example is empty function, the second loops ten times to do 
three additions, in order to run **any** python code.

+-----------+--------------+---------------------+---------------------+
| benchmark | pure python  | jitpy               | numba               |
+-----------+--------------+---------------------+---------------------+
| return 1  | 0.09s (1.0x) | 0.58s (6.4x slower) | 0.36s (4x slower)   |
+-----------+--------------+---------------------+---------------------+
| loop 10   | 0.95s (1.0x) | 0.8s (1.2x faster)  | 0.39s (2.4x faster) |
+-----------+--------------+---------------------+---------------------+

While an interesting data point, this generally points out you should not
write very tiny functions using those layers, but as soon as there is any
work done, CPython is just very slow. For a comparison, running this example
under PyPy gives 0.003s (30x speedup) and 0.11s (8.6x speedup), which means
that if you have a high granularity of functions that can't be nicely separated,
a wholesome solution like PyPy gives more benefits.

The `array benchmark`_ gives ....

.. _`nightlies`: http://buildbot.pypy.org/nightly/trunk/
.. _`numba`: http://numba.pydata.org/
.. _`basic benchmark`: xxx
.. _`array benchmark`: xxx

* :ref:`genindex`
* :ref:`search`
