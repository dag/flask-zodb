from setuptools import setup

setup(
    name='Flask-ZODB',
    version='0.1',

    packages=['flaskext'],
    namespace_packages=['flaskext'],

    install_requires=[
        'Flask',
        'ZODB3',
        'repoze.zodbconn',
    ],

    zip_safe=False,
)
