.. _insight:

Cloud Enrichment Tasks
========================

.. _enrichment_result_schemas:

Enrichment result object schemas
--------------------------------

You can make enrichment using object schema
that defines attribute composition of the objects and data types of the attributes
(see :ref:`data_model` for more information).

To create enrichment tasks, you will need to specify the schema id of the objects that are the results of these tasks.

In the example bellow we get list of enrichment result object schemas.

.. literalinclude:: ../../examples/get_enrichment_results_schemas_chained.py

And one more example of getting schema by ID.

.. literalinclude:: ../../examples/get_enrichment_results_schema.py
