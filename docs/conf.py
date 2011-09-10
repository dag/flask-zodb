import sys, os
sys.path.append(os.path.abspath('_themes'))

import pkg_resources


project = u'Flask-ZODB'
copyright = u'2011, Dag Odenhall'

release = pkg_resources.get_distribution(project).version
version = release.split('dev', 1)[0]


master_doc = 'index'
add_module_names = False
default_role = 'py:obj'


extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']

intersphinx_mapping = {
    'http://docs.python.org/': None,
    'http://flask.pocoo.org/docs/': None,
    'http://werkzeug.pocoo.org/docs/': None,
    'http://zodb.readthedocs.org/en/latest/': None,
}

html_compact_lists = False
html_static_path = ['_static']
html_theme_path = ['_themes']
html_theme = 'flask_small'
html_theme_options = {
    'index_logo': 'flask-zodb.png',
    'github_fork': 'dag/flask-zodb',
}
