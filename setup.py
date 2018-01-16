from setuptools import setup

__version__ = '0.2'

setup(
    name='RestResponse',
    version=__version__,
    description='A fluent python object for interfacing with RESTful JSON APIs.',
    url='https://github.com/MobiusWorksLLC/RestResponse.git',
    author='Tyson Holub',
    author_email='tholub@mobiusworks.com',
    license='MIT',
    packages=['RestResponse'],
    install_requires=[
        'simplejson',
        'six'
    ]
)
