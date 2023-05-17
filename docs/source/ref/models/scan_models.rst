.. _guide_models_scan:

***********
Scan Models
***********

In this document, we will discuss two Django models, :class:`Scan` and
:class:`ScanTask`. These models represent a scanning system that scans
for vulnerabilities in mobile applications. The :class:`Scan` model represents
a single scan, and the :class:`ScanTask` model represents a task within that
scan. We will provide an overview of the models and explain their fields and
methods in detail.

.. autoclass:: mastf.MASTF.models.Scan
    :members:
    :exclude-members: MultipleObjectsReturned, DoesNotExist

.. autoclass:: mastf.MASTF.models.ScanTask
    :members:
    :exclude-members: MultipleObjectsReturned, DoesNotExist

.. TODO: Details