# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../'))


# -- Project information -----------------------------------------------------

project = 'PyUVS'
copyright = '2022, Kyle Connour, Zachariah Milby, and others'
author = 'kconnour and zachariahmilby'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'matplotlib.sphinxext.mathmpl',
    'matplotlib.sphinxext.plot_directive',
    'sphinx_gallery.gen_gallery'
]

# Add any paths that contain graphics here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    "collapse_navigation": True,
    "github_url": "https://github.com/kconnour/PyUVS",
    "header_links_before_dropdown": 8
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# This allows me to write docstrings in __init__
autoclass_content = 'both'
#autodoc_typehints = 'description'  # Only show typehints in the description,
# not the signature
autodoc_member_order = 'bysource'  # Document properties in order


# This displays "ArrayLike" instead of "numpy.typing.ArrayLike"
autodoc_type_aliases = {
    'ArrayLike': 'ArrayLike'
}
autodoc_preserve_defaults = True

# Sphinx gallery stuff
sphinx_gallery_conf = {
    'examples_dirs': '../examples',
    'gallery_dirs': '../documentation-source/rst/examples'
}
