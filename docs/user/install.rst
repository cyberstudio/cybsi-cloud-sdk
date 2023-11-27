.. _install:

Installation of Cybsi Cloud SDK
===============================

Latest version and its dependencies
-----------------------------------------------
We host SDK on `PyPI <https://pypi.org/project/cybsi-cloud-sdk/>`_.

To install it from registry, simply run the following command in your terminal of choice:

.. code-block:: console

  $ pip3 install cybsi-cloud-sdk

You can also get a specific version by running a command like ``pip3 install cybsi-cloud-sdk==1.0.7``.

If you use Poetry to manage your dependencies, add the following sections to your `pyproject.toml` file:

.. code-block:: toml

    ....
    [tool.poetry.dependencies]
    cybsi-cloud-sdk = "1.0.7" # See last version of Cybsi Cloud SDK
    ...

Source code
-----------

.. code-block:: console

  $ git clone git@github.com:cyberstudio/cybsi-cloud-sdk.git

Once you have a copy of the source, you can embed it in your own Python package, or install it into your site-packages easily:

.. code-block:: console

  $ cd cybsi-cloud-sdk
  $ python -m pip install .
