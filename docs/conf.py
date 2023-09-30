# -*- coding: utf-8 -*-
# Cybsi Cloud SDK documentation build configuration file.

import sys
import os

# Insert Cybsi Cloud SDK path into the system.
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("_themes"))

import cybsi  # noqa: E402


# -- General configuration ------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "enum_tools.autoenum",
    "sphinxjp.themes.basicstrap",
]

# A list of regular expressions that match anchors Sphinx should skip
# when checking the validity of anchors in links.
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-linkcheck_anchors_ignore
linkcheck_anchors_ignore = [
    "/artifacts/browse/tree/General/cybsi-cloud-pypi"  # anchor of link to pt artifactory
]

templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = u"Cybsi Cloud SDK"
copyright = u"Cybsi Cloud developers"
author = u"Cybsi Cloud developers"
version = cybsi.__version__
release = cybsi.__version__
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# Warn about all references where the target cannot be found.
nitpicky = True
nitpick_ignore = [
    ("py:class", "T"),  # Ignore classic typevar
    ("py:obj", "cybsi.cloud.api.T"),  # https://github.com/sphinx-doc/sphinx/issues/9705
    ("py:obj", "cybsi.cloud.pagination.T"),  # https://github.com/sphinx-doc/sphinx/issues/9705
    ("py:class", "httpx.Response"),
    ("py:class", "enum.EnumMeta"),
    ("py:class", "typing.AbstractContextManager"),
    ("py:class", "typing.AbstractAsyncContextManager"),
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "colorful"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

html_theme = 'basicstrap'
html_theme_options = {
    'sidebar_span': 1,
}
html_static_path = ["_static"]

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = False

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    "index": ["sidebar.html", "sourcelink.html", "searchbox.html"],
    "**": [
        "sidebar.html",
        "localtoc.html",
        "relations.html",
        "sourcelink.html",
        "searchbox.html",
    ],
}

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

html_search_language = 'en'

# Output file base name for HTML help builder.
htmlhelp_basename = "cybsisdkdoc"

# -- Options for LaTeX output ---------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "cybsi.tex", u"Cybsi Cloud SDK Documentation",
     author, "manual")
]

# LaTeX document customization
latex_elements = {
    # \\usepackage[X2,T1]{fontenc} if you need Cyrillic letters (Cybsi работает)
    'fontenc': '\\usepackage[T1]{fontenc}'
}

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, "cybsi_sdk", u"Cybsi Cloud SDK Documentation",
     [author], 1)]

# -- Options controlling document structure --------------------------------
autodoc_member_order = 'bysource'


# -- Options for type hints in developer documentation ---------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

autodoc_typehints = 'none'
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True
napoleon_use_ivar = True
typehints_document_rtype = True
typehints_fully_qualified = False
always_document_param_types = False
