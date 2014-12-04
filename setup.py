

if __name__ == '__main__':
  from setuptools import setup, Feature, Extension
  setup(
    name='jitpy',
    description='A library to embed PyPy in CPython.',
    long_description="""
jitpy
=====

A library that let's you embed PyPy into CPython.
Please see the `Documentation <http://jitpy.readthedocs.org/>`_.

Contact
-------

`Mailing list <https://groups.google.com/forum/#!forum/jitpy>`_
    """,
    version='0.1',
    packages=['jitpy'],
    zip_safe=False,

    url='http://jitpy.readthedocs.org',
    author='Maciej Fijalkowski',
    author_email='jitpy@googlegroups.com',

    license='MIT',

    features={
    },

    install_requires=[
    ]
  )

