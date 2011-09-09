"""
Flask-ZODB
----------

.. image:: http://packages.python.org/Flask-ZODB/_static/flask-zodb.png

Transparent and scalable persistence of Python objects for Flask
applications.  Use it as your database or as a complement to another
database - for example PostgreSQL where you need to perform rich queries
and ZODB where you need structured data and mapping to and from Python
types is inconvenient.

::

    app = Flask(__name__)
    db = ZODB(app)

    @app.before_request
    def set_db_defaults():
        if 'entries' not in db:
            db['entries'] = List()

    @app.route('/')
    def show_entries():
        return render_template('show_entries.html', entries=db['entries'])


    @app.route('/add', methods=['POST'])
    def add_entry():
        db['entries'].append(request.form)
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))

"""

from setuptools import setup

setup(
    name='Flask-ZODB',
    version='0.2',
    url='https://github.com/dag/flask-zodb',

    license='BSD',
    author='Dag Odenhall',
    author_email='dag.odenhall@gmail.com',

    description='Use the ZODB with Flask',
    long_description=__doc__,
    keywords=['flask', 'zodb', 'persistence', 'database'],

    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,

    requires=['flask (>=0.7)', 'ZODB', 'zodburi'],
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
