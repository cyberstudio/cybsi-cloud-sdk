.. _filebox:

Cloud File Storage
========================

Cybsi Cloud provides the API to store files. The files could be used for enrichment, etc.

The easiest way to upload a file is using the `upload` method.

 .. literalinclude:: ../../examples/file_upload.py

Also there is a low-level API to upload files by parts. It can be used to implement parallel file uploading.

 .. literalinclude:: ../../examples/file_upload_parts.py

To download the file use the `download` method:

 .. literalinclude:: ../../examples/file_download.py