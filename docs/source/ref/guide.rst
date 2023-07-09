.. _ref_guide:

************
Visual Guide
************

*Work in progress*

Projects
--------

The MAST-Framework offers users to create projects in order to organize scans of a specific
app. Each project may contain multiple scans for multiple files and it stores the detected
software packages for all uploaded app files. The directory structure of a simple project
can be summarized to the following:

.. code-block:: text

    projects/
        <uuid:project_uuid>/
            <str:internal_name>.[apk|ipa]
            semgrep-<internal_name>.json
            libscout-<internal_name>.json
            <internal_name>/
                info.json # PlayStore, AppStore information
                src/
                    [ java/ ]
                    [ smali/ ]
                contents/
                    # initial ZIP-File data

.. note::
    The internal name will be generated based on the MD5 hash value of the uploaded file's name
    and the current datetime:

    .. code-block:: bnf

        internal_name := MD5(uploaded_file.name) "_" DATETIME.now


Bundles
-------

*TODO*

ScanTask design
---------------

After a new scan has been requested, it will be executed on the target scan date. Before each
scanner is executed, there is a preparation task, that is called asynchronously:

1. Preparation: create directories, extract ZIP Files, decompile binaries
2. Call Plugins: each scanner comes with a ``task`` field that should be a function that takes a ``Scan`` and ``ScanTask`` object as input.



