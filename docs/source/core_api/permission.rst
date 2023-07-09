.. _core_api_permissions:

***************
App Permissions
***************

.. autoclass:: mastf.core.files.apl.PermissionDefItem
    :members:

.. autoclass:: mastf.core.files.apl.GroupDefItem
    :members:

.. autoclass:: mastf.core.files.apl.AppPermissionList
    :members:

Example Usage
-------------

.. code-block:: python

    from mastf.core.files import apl
    with open("permissions.apl", "r") as fp:
        x = apl.parse(fp)

    x.groups # list of GroupDefItem
    x.permissions # ungrouped permission definitons


.. autofunction:: mastf.core.files.apl.parse

.. autofunction:: mastf.core.files.apl.load