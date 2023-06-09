.. _api:

Developer Interface
===================

.. module:: cybsi

This part of the documentation covers all the public interfaces of Cybsi Cloud SDK.

Low-level client
----------------

Client interface
~~~~~~~~~~~~~~~~
.. autoclass:: cybsi.cloud.Client
    :members:

.. autoclass:: cybsi.cloud.AsyncClient
    :members:

Client configuration
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: cybsi.cloud.Config
    :members:
.. autoclass:: cybsi.cloud.Limits
.. autoclass:: cybsi.cloud.Timeouts


Auth & API-Keys
~~~~~~~~~~~~~~~
.. autoclass:: cybsi.cloud.auth.APIKeyAuth

.. automodule:: cybsi.cloud.auth
    :members:
    :imported-members:
    :inherited-members:
    :exclude-members: APIKeyAuth

IOCean
~~~~~~
.. automodule:: cybsi.cloud.iocean
    :members:
    :imported-members:
    :inherited-members:

Common views and data types
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: cybsi.cloud.Null
.. autoclass:: cybsi.cloud.Nullable
.. autoclass:: cybsi.cloud.NullType
.. autoclass:: cybsi.cloud.Tag
.. autoclass::  cybsi.cloud.CybsiAPIEnum
     :members:

Pagination
~~~~~~~~~~
.. automodule:: cybsi.cloud.pagination
    :members:
    :inherited-members:

Exceptions
----------

.. automodule:: cybsi.cloud.error
    :members:
    :show-inheritance:

API Changes
-----------

Breaking API changes are documented here. There's no such changes yet.

Licensing
---------

TBD
