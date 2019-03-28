"""
Flask-OASchema
----------

A Flask extension for validating JSON requests against OAS type jsonschema

"""
from setuptools import setup


setup(
    name='Flask-OASSchema',
    version='0.9.8',
    url='https://github.com/IlyaSukhanov/flask-oasschema',
    license='MIT',
    author='Ilya Sukhanov',
    author_email='ilya@sukhanov.net',
    description='Flask extension for validating JSON requests',
    long_description=__doc__,
    py_modules=['flask_oasschema'],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.9',
        'jsonschema>=1.1.0',
        'future>=0.16.0',
    ],
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ])
