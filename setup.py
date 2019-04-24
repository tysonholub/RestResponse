import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


__version__ = '2.1.0'

setup(
    name='RestResponse',
    version=__version__,
    description='A fluent python object for interfacing with RESTful JSON APIs.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/tysonholub/RestResponse.git',
    author='Tyson Holub',
    author_email='tyson@tysonholub.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'simplejson',
        'six',
        'SQLAlchemy',
        'cloudpickle'
    ]
)
