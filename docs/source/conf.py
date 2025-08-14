import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))

project = 'MC-DCaRE'
copyright = '2025, Your Name'
author = 'Your Name'
release = '1.0'

extensions = [
    'recommonmark',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'

html_theme = 'alabaster'
html_static_path = ['_static']
