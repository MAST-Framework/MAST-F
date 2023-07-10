from __future__ import annotations

import plistlib
import io

__all__ = ["PropertyList"]

class PropertyList(dict):
    """Wrapper class for iOS PropertyList (.plist) files."""

    def __init__(self, meta: dict = None, fp: str | bytes | io.IOBase = None) -> None:
        self.update(meta or {})
        if isinstance(fp, (str, bytes)):
            self.loads(fp)
        elif isinstance(fp, io.IOBase):
            self.load(fp)

    def loads(self, text: str | bytes) -> None:
        """Parses the given bytes and imports the key-value pairs"""
        if not text:
            return

        self.update(plistlib.loads(text))

    def load(self, fp: io.IOBase) -> None:
        """Parses the given file and imports all key-value pairs"""
        if not fp:
            return

        self.update(plistlib.load(fp))

    def get_property(self, key: str, default=None, type_=None):
        """Returns the stored property mapped to the given key.

        :param key: the property key
        :type key: str
        """
        value = self.get(key, default)
        if value is not None and type_ is not None:
            if not isinstance(value, type_):
                raise TypeError(f"Invalid type: {type(value)} != {type_}")
        elif value is None:
            return default

        return value

    def get_list(self, key: str) -> list:
        """Returns a list mapped to the given key.

        This method fails when the mapped value is not a list or tuple.

        :param key: the property key
        :type key: str
        :return: the property value
        :rtype: list
        """
        return self.get_property(key, default=[], type_=list)

    def get_dict(self, key: str) -> dict:
        """Returns a dict mapped to the given key.

        This method fails when the mapped value is not a list or tuple.

        :param key: the property key
        :type key: str
        :return: the property value or empty if this property is not present
        :rtype: dict
        """
        return self.get_property(key, default={}, type_=dict)

    @property
    def display_name(self) -> str:
        return self.get_property("CFBundleDisplayName")

    @property
    def bundle_name(self) -> str:
        return self.get_property("CFBundleName")

    @property
    def bundle_version(self) -> str:
        return self.get_property("CFBundleVersion")

    @property
    def bundle_version_string(self) -> str:
        return self.get_property("CFBundleShortVersionString")

    @property
    def transport_security(self) -> dict:
        return self.get_property("NSAppTransportSecurity")

    @property
    def bundle_id(self) -> str:
        return self.get_property("CFBundleIdentifier")

    @property
    def platform_version(self) -> str:
        return self.get_property("DTPlatformVersion")

    @property
    def min_os_version(self) -> str:
        return self.get_property("MinimumOSVersion")

    def get_declared_permissions(self) -> dict[str, str]:
        """Returns all properties with 'UsageDescription' in their names.

        :return: a dict of permissions with their usage description. Note that
                 the 'UsageDecription' identifier will be removed
        :rtype: dict
        """
        permissions = {}
        for key, value in self.items():
            # Important - https://developer.apple.com/documentation/contacts
            # "An iOS app linked on or after iOS 10 needs to include in its
            # Info.plist file the usage description keys for the types of data
            # it needs to access or it crashes. To access Contacts data
            # specifically, it needs to include NSContactsUsageDescription."
            if key.endswith("UsageDescription"):
                name = key[: -len("UsageDescription")]
                permissions[name] = value
        return permissions
