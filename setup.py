"""
Flask-ZODB
----------

Transparent and scalable persistence of Python objects for Flask
applications.  Use it as your database or as a complement to another
database - for example PostgreSQL where you need to perform rich queries
and ZODB where you need structured data and mapping to and from Python
types is inconvenient.

Usage is completely seamless::

    from flask import Flask, request, redirect, render_template
    from flaskext.zodb import ZODB

    app = Flask(__name__)
    app.config['ZODB_STORAGE'] = 'file://app.fs'
    db = ZODB(app)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            db['shoutout'] = request.form['message']
            return redirect('index')
        else:
            message = db.get('shoutout', 'Be the first to shout!')
            return render_template('index.html', message=message)

"""

from setuptools import setup

setup(
    name='Flask-ZODB',
    version='0.1',
    url='https://github.com/dag/flask-zodb',

    license='BSD',
    author='Dag Odenhall',
    author_email='dag.odenhall@gmail.com',

    description='Use the ZODB with Flask',
    long_description=__doc__,

    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,

    install_requires=[
        'Flask>=0.7',
        'zodburi',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: ZODB',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
