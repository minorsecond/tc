from distutils.core import setup

import py2exe


setup(
    name='Pyper Timeclock Utility',
    version='v0.1',
    packages=['tests', 'tests.db', 'models', 'sqa_uuid', 'get_weekks'],
    url='',
    license='GPLv2.0',
    author='Robert Ross Wardrup',
    author_email='minorsecond@gmail.com',
    description='',
    console=['tc.py']
)
