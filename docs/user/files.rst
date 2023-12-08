.. _filebox:

Cloud File Storage
========================

Cybsi Cloud provides the API to store files. The files could be used for enrichment, etc.

Use multipart upload API for files smaller than 50 MiB to upload in one request:

 .. literalinclude:: ../../examples/file_multipart_upload.py

To download the file use the code below:

 .. literalinclude:: ../../examples/file_download.py