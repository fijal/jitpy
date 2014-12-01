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
have very different characteristics. A simple example::

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

