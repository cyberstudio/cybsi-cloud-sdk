.. _quickstart:

Quickstart
==========

Eager to get started? This page gives a good introduction in how to get started
with Cybsi Cloud SDK.

First, make sure that:

* Cybsi Cloud SDK is :ref:`installed <install>` and up-to date.


Let's get started with some simple examples.

.. _get_collection_objects_chained:

Get objects from collection
---------------------------
Cybsi Cloud serves threat intelligence. In our case threat intelligence is condensed into collections of objects.
Often such objects represent `indicators of compromise <https://en.wikipedia.org/wiki/Indicator_of_compromise>`_.

In other words, Cybsi Cloud has collections of objects associated with malicious software, phishing sites, botnets and so on. It also has collections of definitely harmless files, IP addresses and domain names.

In the example below we get list of object from the collection named "phishing".

.. literalinclude:: ../../examples/get_collection_objects_chained.py

Use AsyncClient instead of Client if you have an asynchronous application.

.. _get_collection_objects_changes:

Get object changes in the collection
------------------------------------

In the example below we get objects changes happened in the collection.

.. literalinclude:: ../../examples/get_collection_objects_changes.py

.. _working_with_tasks:

Working with tasks
------------------

You also can working with enrichment tasks. Create tasks for enriching indicators and get their results.
The results of the enrichment are objects corresponding to a given schema.

See :ref:`enrichment tasks examples <insight>` for more information.