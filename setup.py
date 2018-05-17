import os
from setuptools import setup, find_packages

__version__ = '0.4.6'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='RestResponse',
    version=__version__,
    description='A fluent python object for interfacing with RESTful JSON APIs.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/MobiusWorksLLC/RestResponse.git',
    author='Tyson Holub',
    author_email='tholub@mobiusworks.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'simplejson',
        'six',
        'SQLAlchemy'
    ]
)
