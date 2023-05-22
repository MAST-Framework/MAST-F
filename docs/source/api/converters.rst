.. _api_converters:

**********
Converters
**********

.. automodule:: mastf.MASTF.converters

The following default converters will be registered on application start:

.. list-table:: Default Converters
    :header-rows: 1
    :widths: 10, 10, 10

    * - Class
      - URL name
      - Regex
    * - :class:`FindingTemplateIDConverter`
      - findingtemplateid
      - ``r"FT-[\w-]{36}-[\w-]{36}"``
    * - :class:`VulnerabilityIDConverter`
      - vulnerabilityid
      - ``r"SV-[\w-]{36}-[\w-]{36}"``
    * - :class:`FindingIDConverter`
      - findingid
      - ``r"SF-[\w-]{36}-[\w-]{36}"``
    * - :class:`MD5Converter`
      - md5
      - ``r"[0-9a-fA-F]{32}"``
    * - :class:`HostIDConverter`
      - hostid
      - ``r"hst_[\dA-Za-z-]{36}"``
    * - :class:`ComponentIdConverter`
      - componentid
      - ``r"cpt_[\dA-Za-z-]{36}"``
    * - :class:`DependencyIdConverter`
      - dependencyid
      - ``r"([0-9a-fA-F]{32}){2}"``

----------
Components
----------

.. autoclass:: mastf.MASTF.converters.StringConverter
    :members:

.. autofunction:: mastf.MASTF.converters.listconverters
