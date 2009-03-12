from setuptools import setup

setup(name='typedbytes',
      version='0.3.3',
      description='A Python module for dealing with so called "typed bytes"',
      author='Klaas Bosteels',
      author_email='klaas@last.fm',
      url='http://github.com/klbostee/typedbytes',
      py_modules=['typedbytes'],
      test_suite='nose.collector',
      tests_require=['nose']
     )
