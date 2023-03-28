from mastf.MASTF.scanners.plugin import ScannerPlugin, Plugin, Extension

@Plugin
class SASTScannerPlugin(ScannerPlugin):

    name = "SAST"
    help = "Static Application Security Testing (Basic Scan)"
    title = "SAST Scanner"

    extensions = [
        # The app's or file's details will be displayed with this
        # extension enabled
        Extension.EXT_DETAILS,

        # To view the app's permissions, this extension is required
        Extension.EXT_PERMISSIONS,

        # The most common extension will be the view of vulnerabilities
        # as it stored detailed information about each finding.
        Extension.EXT_VULNERABILITIES,

        # Same as vulnerability extension, but there is not grouping
        # by language (and secure results can be included as well)
        'findings',
        
        Extension.EXT_HOSTS,
    ]
    

@Plugin
class TestScannerPlugin(ScannerPlugin):

    name = "Test"
    help = "Test Scanner"
    title = "Test Scanner"

    extensions = [
        # The app's or file's details will be displayed with this
        # extension enabled
        Extension.EXT_DETAILS,

        # To view the app's permissions, this extension is required
        Extension.EXT_PERMISSIONS,

        # The most common extension will be the view of vulnerabilities
        # as it stored detailed information about each finding.
        Extension.EXT_VULNERABILITIES,

        # Same as vulnerability extension, but there is not grouping
        # by language (and secure results can be included as well)
        'findings',
    ]
    


