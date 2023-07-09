.. _api_scanner_plugin

**************
Scanner Plugin
**************

Basics
======

.. autofunction:: mastf.MASTF.scanners.plugin.Plugin

.. autoclass:: mastf.MASTF.scanners.plugin.Extension
    :members:

.. autoclass:: mastf.MASTF.scanners.plugin.ScannerPlugin
    :members:

.. autoclass:: mastf.MASTF.scanners.plugin.ScannerPluginTask
    :members:

Default Mixins
==============

.. autoclass:: mastf.MASTF.scanners.mixins.DetailsMixin
    :members:

.. autoclass:: mastf.MASTF.scanners.mixins.PermissionsMixin
    :members:

.. autoclass:: mastf.MASTF.scanners.mixins.VulnerabilitiesMixin
    :members:

.. autoclass:: mastf.MASTF.scanners.mixins.FindingsMixins
    :members:

.. autoclass:: mastf.MASTF.scanners.mixins.HostsMixin
    :members:

.. autoclass:: mastf.MASTF.scanners.mixins.ComponentsMixin
    :members:


Android Plugin
==============

.. autoclass:: mastf.MASTF.scanners.android_sast.AndroidTask
    :members:

.. autoclass:: mastf.MASTF.scanners.android_sast.AndroidScannerPlugin
    :members:

Android Scan Tasks
------------------

.. autofunction:: mastf.MASTF.scanners.android_sast.app_info_scan.get_app_info

.. autofunction:: mastf.MASTF.scanners.android_sast.app_info_scan.get_app_net_info

.. autoclass:: mastf.MASTF.scanners.android_sast.app_info_scan.NetworkSecurityHandler
    :members:

.. autofunction:: mastf.MASTF.scanners.android_sast.manifest_scan.get_manifest_info

.. autofunction:: mastf.MASTF.scanners.android_sast.manifest_scan.run_manifest_scan

.. autoclass:: mastf.MASTF.scanners.android_sast.manifest_scan.AndroidManifestHandler
    :members:


SAST Interface
==============

.. autofunction:: mastf.MASTF.scanners.code.yara_scan_file

.. autofunction:: mastf.MASTF.scanners.code.yara_code_analysis

.. autofunction:: mastf.MASTF.scanners.code.sast_scan_file

.. autofunction:: mastf.MASTF.scanners.code.sast_code_analysis

.. autofunction:: mastf.MASTF.scanners.code.add_finding

.. autoclass:: mastf.MASTF.scanners.code.YaraResult
    :members:
