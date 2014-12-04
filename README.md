jitpy
=====

Library to embed PyPy into CPython. See
[documentation](http://jitpy.readthedocs.org) for more examples.

The simplest example:

    from jitpy.wrapper import jittify

    @jittify([int, float], float)
    def func(count, no):
        s = 0
        for i in range(count):
           s += no
        return s

    func(100000000, 1.2)

Runs about 20x faster.

MIT Licensed.
