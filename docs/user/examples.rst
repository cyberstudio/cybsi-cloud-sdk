.. _examples:

Examples
========

.. _register-object-schema-example:

Register object schema
----------------------

See :ref:`object_schemas` for information about schemas

In the example below we registering JSON Schema of object.

.. literalinclude:: ../../examples/register_object_schema.py

.. _add_collection_object:

Add object to collection
------------------------

See :ref:`object_schemas` for information about schemas

In the example below we add object to collection.

.. literalinclude:: ../../examples/add_collection_object.py

.. _delete_collection_object:

Delete object from collection
-----------------------------

In the example below we delete object from collection.

.. literalinclude:: ../../examples/delete_collection_object.py

.. _pagination-example:

Pagination
----------

You'll often need to work with collections of elements API provides.

Cybsi Cloud SDK provides two ways to traverse collections.

The **first** way is pages traversing.
This approach fits for cases when you need to get page's properties i.e. cursor.
For walking by page elements just iterate through the page.

.. literalinclude:: ../../examples/pagination_manual.py

The **second** way is elements traversing. This approach allows you to iterate through
collections without working with pages. To work with collections as with iterator use `chain_pages`.

.. literalinclude:: ../../examples/get_collection_objects_chained.py
