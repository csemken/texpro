# Configuration file for the Sphinx documentation builder.


# -- Project information -----------------------------------------------------

project = 'TeXpro'
copyright = '2021, Christoph Semken'
author = 'Christoph Semken'


# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx_rtd_theme',
    'nbsphinx',
]

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']
