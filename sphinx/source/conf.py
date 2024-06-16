# conf.py

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

# Project information
project = 'My FastAPI Project'
author = 'Your Name'
release = '0.1'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

# Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Additional settings for type hints
autodoc_typehints = 'description'
