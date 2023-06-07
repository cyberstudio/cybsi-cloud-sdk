.. _advanced:

Advanced Usage
==============

This document covers some of Cybsi Cloud SDK more advanced features.

Timeouts and limits
-------------------

You can explicitly configure connect/read/write timeouts and maximum of number connection for Client through the Config data class.

In the example below you can see how it can be used:

.. literalinclude:: ../../examples/client_advanced_config.py

.. _auth_api_keys_chained:

Get api keys
------------

In the example below we get api keys list.

.. literalinclude:: ../../examples/auth_api_keys_chained.py

.. _auth_generate_api_key:

Generate api key
----------------

In the example below we generate new api key.

.. literalinclude:: ../../examples/auth_generate_api_key.py

.. _auth_resources_chained:

Get resources
-------------

In the example below we get resources list.

.. literalinclude:: ../../examples/auth_resources_chained.py

