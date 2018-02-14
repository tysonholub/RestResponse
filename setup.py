from setuptools import setup, find_packages

__version__ = '0.4.2'

setup(
    name='RestResponse',
    version=__version__,
    description='A fluent python object for interfacing with RESTful JSON APIs.',
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
