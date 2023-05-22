# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os
import re

project = u'MAST-Framework'
slug = re.sub(r"\W+", '-', project.lower())
copyright = u'2023, MatrixEditor'
author = 'MatrixEditor'
language = "en"


version = '0.1'
release = '0.0.1-alpha'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../..'))

# Specify settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastf.MASTF.settings')

# Setup Django
import django
django.setup()

extensions = [
    'sphinx.ext.autodoc',
	'sphinx.ext.doctest',
	'sphinx.ext.todo',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']

# The master toctree document.
master_doc = 'index'

# The suffix of source filenames.
source_suffix = '.rst'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'README.rst']
mock_imports = ['django']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'
html_favicon = "favicon.ico"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'navigation_depth': 4,
    # Toc options
    'collapse_navigation': False,
    'titles_only': False
}
