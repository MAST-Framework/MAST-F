.. _api_permissions:


*****************
Permission System
*****************

.. automodule:: mastf.MASTF.permissions

There will be some (by now only one) default permissions that can't be created
at runtime:

- ``CanCreateUser``: Used to determine whether a user can create other users

Default runtime permissions are:

.. list-table:: Default Runtime Permissions
    :header-rows: 1
    :widths: 10, 10, 10, 20

    * - Name
      - Model
      - HTTP Methods
      - Description
    * - CanEditTeam
      - :class:`Team`
      - ``PATCH``, ``PUT``
      - Users with this permission will be able to update team related data
    * - CanViewTeam
      - :class:`Team`
      - ``GET``
      - Users with this permission will be able to view team related data
    * - CanDeleteTeam
      - :class:`Team`
      - ``DELETE``
      - Users with this permission will be able to delete a spcific team
    * - CanEditProject
      - :class:`Project`
      - ``PATCH``, ``GET``
      - With this permission users are able to view and update a project
    * - CanDeleteProject
      - :class:`Project`
      - ``DELETE``
      - Needed to delete a project
    * - CanEditUser
      - :class:`User`
      - ``PATCH``, ``GET``
      - This permission can be used to update user-data, **NOT** account-data
    * - CanDeleteUser
      - :class:`User`
      - ``DELETE``
      - Needed to delete a user
    * - CanEditAccount
      - :class:`Account`
      - ``PATCH``, ``GET``
      - This permission can be used to update account-data, **NOT** user-data
    * - CanDeleteAccount
      - :class:`Account`
      - ``DELETE``
      - Needed to delete an account
    * - CanBundleTeam
      - :class:`Bundle`
      - ``PATCH``, ``PUT``
      - Users with this permission will be able to update bundle related data
    * - CanViewBundle
      - :class:`Bundle`
      - ``GET``
      - Users with this permission will be able to view bundle related data
    * - CanDeleteBundle
      - :class:`Bundle`
      - ``DELETE``
      - Users with this permission will be able to delete a spcific bundle

-------
Classes
-------

.. autoclass:: mastf.MASTF.permissions._Method
    :members:

.. autoclass:: mastf.MASTF.permissions.BoundPermission
    :members: