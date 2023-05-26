.. _install:

Installation of Cybsi Cloud SDK
===============================

Latest version and its dependencies
-----------------------------------------------
We host SDK on private PyPI registry.

To install it from registry, simply run the following command in your terminal of choice:

.. code-block:: console

  $ pip3 install cybsi-cloud-sdk \
  --index-url https://repo.ptsecurity.ru/artifactory/api/pypi/cybsi-cloud-pypi/simple/ \
  --trusted-host repo.ptsecurity.ru

You can also get a specific version by running a command like ``pip3 install cybsi-cloud-sdk==0.0.1``.

If you use Poetry to manage your dependencies, add the following sections to your `pyproject.toml` file:

.. code-block:: toml

    ....
    [tool.poetry.dependencies]
    cybsi-cloud-sdk = "0.0.1" # See last version of Cybsi Cloud SDK

    [[tool.poetry.source]]
    name = "cybsi-cloud-sdk"
    url = "https://repo.ptsecurity.ru/artifactory/api/pypi/cybsi-cloud-pypi/simple/"
    ...

Source code
-----------

.. code-block:: console

  $ git clone git@gitlab.ptsecurity.com:cybsi/cloud-python-sdk.git

Once you have a copy of the source, you can embed it in your own Python package, or install it into your site-packages easily:

.. code-block:: console

  $ cd cloud-python-sdk
  $ python -m pip install .
