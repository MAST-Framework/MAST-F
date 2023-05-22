.. _ref_guide:

************
Visual Guide
************

*Work in progress*

Project-Directory Structure
---------------------------

The directory structure of a simple project can be summarized to the following:

.. code-block:: text
    projects/
        <uuid:project_uuid>/
            uploadedFile.[apk|ipa]
            <md5:file_md5>/
                src/
                    [ java/ ]
                    [ smali/ ]
                    [ swift/ ]
                    [ assembler/ ]
                contents/
                    # initial ZIP-File data


ScanTask design
---------------

After a new scan has been requested, it will be executed on the target scan date. Before each
scanner is executed, there is a preparation task, that is called asynchronously:

1. Preparation: create directories, extract ZIP Files, decompile binaries
2. Call Plugins: each scanner comes with a ``task`` field that should be a function that takes a ``Scan`` and ``ScanTask`` object as input.



