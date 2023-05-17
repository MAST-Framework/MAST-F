.. _ref_tech:

***********************
List of used Frameworks
***********************

In this documentation page, we will provide basic information about the frameworks used
in this project. Note that the following table won't include transient dependencies.
Container services won't be included as well as they can be changed by any user to fit
his requirements.

.. list-table:: Used frameworks and dependencies (backend)
    :header-rows: 1
    :widths: 20, 10, 20

    * - Dependency/ Framework
      - Version
      - Usage
    * - `Python`_
      - ``3.8.10`` (min) to ``3.11``
      - Programming language
    * - `Docker Engine`_
      - ``23.0.5``
      - Container deployment
    * - `Docker Compose`_
      - ``2.17.3``
      - Container build system
    * - `Django`_
      - ``4.2.1``
      - Web framework
    * - `Django REST Framework`_
      - ``3.14.0``
      - Extension to the web framework
    * - `Celery`_
      - ``5.2.7``
      - Asynchronous task queue
    * - `YARA`_
      - ``4.0.5``
      - Malware and Vulnerability detection rules
    * - `Yara Scanner Server`_ (YSS)
      - ``2.0.3``
      - Yara scanner and server
    * - (`Sphinx`_)
      - ``6.2.1``
      - Documentation builder


.. list-table:: Used frameworks and dependencies (frontend)
    :header-rows: 1
    :widths: 20, 10, 20

    * - Dependency/ Framework
      - Version
      - Usage
    * - `jQuery`_ + `jQuery DataTables`_
      - ``3.6.4``, ``1.13.4``
      - Table integration and HTML manipulation
    * - `jsTree`_
      - ``3.2.1``
      - Display source trees
    * - `ApexCharts`_
      - ``3.36.2``
      - Generate charts
    * - `Enlighterjs`_
      - ``3.7.0``
      - Highlight source code
    * - `jsVectormap`_
      - ``-``
      - Display maps
    * - `Tabler Theme`_
      - ``v1.0.0-beta17``
      - Global HTML/CSS theme
    * - `JetBrains UI Kit`_ (Icons only)
      - ``-``
      - Source tree icons
    * - `Celery Progress`_
      - ``0.3``
      - Display celery task updates


.. _Docker Engine: https://www.docker.com/
.. _Docker Compose: https://docs.docker.com/compose/
.. _Python: https://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _Django REST Framework: https://www.django-rest-framework.org/
.. _Yara Scanner Server: https://github.com/ace-ecosystem/yara_scanner
.. _YARA: https://yara.readthedocs.io/en/stable/index.html
.. _Tabler Theme: https://tabler.io
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _JetBrains UI Kit: https://jetbrains.design/intellij/
.. _Celery Progress: https://github.com/czue/celery-progress/blob/master/celery_progress/static/celery_progress/celery_progress.js
.. _jQuery: https://jquery.com/
.. _jQuery DataTables: https://datatables.net/
.. _jsTree: https://www.jstree.com/
.. _ApexCharts: https://apexcharts.com/
.. _Enlighterjs: https://github.com/EnlighterJS/EnlighterJS
.. _jsVectormap: https://github.com/themustafaomar/jsvectormap
.. _celery: https://docs.celeryq.dev/en/stable/getting-started/introduction.html


