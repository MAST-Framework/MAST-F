"""
Simple module for parsing ADB's output for Android permissions.
"""
import re
import subprocess

from io import IOBase, StringIO, BytesIO


GROUP_TYPE = "group:"
UNGROUPED_TYPE = "ungrouped"
PERMISSION_TYPE = "permission:"

class AndroidPermissions(dict):
    """Management class to store all android permissions of an Android device.

    This class will provide different results according to the used options
    within initialization. There are the following default options:

    - ``package``: Specifies a regular expression to filter the result of ADB
    - ``text``: instead of using the ADB command line utility, the text that
                should be imported/ parsed can be provided by using this parameter.
    - ``adb_path``: Enables this class to use another ADB path
    - ``group``: Groups all permissions by their permission group
    - ``dangerous``: Lists only permissions that are dangerous
    - ``invisible``: Lists permissions that are invisible to the user by default
                     (will be ignored by default)

    The returned permission and permission-group will have the following structure:

    >>> AndroidPermissions.all()
    { \n\
        "identifier": {\n\
            "label": "value" or None or ['protectionLevel1', ...] \n\
        } \n\
    }

    """

    kwargs: dict
    """Additional arguments that should be covered when importing permissions"""

    re_package: re.Pattern = re.compile(r".*")
    """Regex to filter out unnecessary permissions or groups"""

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        re_pkg = self.kwargs.pop("package", None)
        if re_pkg:
            self.re_package = re.compile(re_pkg)

    @property
    def ungrouped(self) -> dict:
        """Returns all permissions that don't belong to any group

        :return: all ungrouped permissions or this instance of no groups are present
        :rtype: dict
        """
        if self.kwargs.get('group', False):
            return self.get('ungrouped', UNGROUPED_TYPE)
        return self

    @staticmethod
    def all(**kwargs) -> 'AndroidPermissions':
        """Returns all Android permissions of a device

        :return: all permissions mapped into JSON objects
        :rtype: AndroidPermissions
        """
        text = kwargs.pop("text", None)

        permissions = AndroidPermissions(**kwargs)
        permissions.load(text)
        return permissions

    def load(self, text: str = None) -> None:
        """Imports the permissions from the given text or vie ADB

        :param text: the permissions to import, defaults to None
        :type text: str, optional
        :raises TypeError: if the text type is invalid
        """
        if text is not None:
            if isinstance(text, (bytearray, bytes)):
                source = BytesIO(text)
            elif isinstance(text, str):
                source = StringIO(text)
            elif isinstance(text, IOBase):
                source = text
            else:
                raise TypeError(f"Invalid source type: {type(text)}")

        else:
            # The command depends on the provided arguments
            cmd = self.make_cmd()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, check=True)
                source = BytesIO(result.stdout)
            except subprocess.CalledProcessError as err:
                # By re-raising this exception the output will provide more details
                raise RuntimeError(err.stderr.decode()) from err

        assert source, (
            "The input source must not be null!"
        )
        self._parse(source)

    def make_cmd(self) -> str:
        """Generates the ADB shell command used to fetch all permissions

        :return: the generated command
        :rtype: str
        """
        adb_path = self.kwargs.get("adb_path", "adb")
        args = []
        if self.kwargs.get("group", False):
            args.append('-g')
        if self.kwargs.get('dangerous', False):
            args.append('-d')
        if not self.kwargs.get('invisible', False):
            args.append('-u')
        return f"{adb_path} shell pm list permissions -f {' .'.join(args)}"

    def _parse(self, text: IOBase) -> None:
        parent = None
        element = None
        while True:
            line = text.readline()
            if len(line) == 0:
                break

            line = line.strip()
            if len(line) == 0:
                continue

            if isinstance(line, (bytes, bytearray)):
                line = line.decode()

            assert isinstance(line, str), (
                "The input line must be of type string"
            )

            if line[0] == '+': # permission or group definition
                identifier = line[1:].strip()
                if identifier.startswith(GROUP_TYPE) or identifier == UNGROUPED_TYPE:
                    identifier = identifier.lstrip(GROUP_TYPE)
                    if self.re_package.match(identifier):
                        parent = {}
                        element = None
                        self[identifier] = parent

                elif identifier.startswith(PERMISSION_TYPE):
                    element = {}
                    identifier = identifier.lstrip(PERMISSION_TYPE)
                    if self.re_package.match(identifier):
                        if parent is not None: # maps the given permission element to a group
                            parent[identifier] = element
                        else:
                            self[identifier] = element

            elif parent is not None or element is not None:
                val: dict = parent if element is None else element
                name, desc = line.split(':')
                if name.lower() == 'protectionlevel':
                    val[name] = desc.split('|') if desc != 'null' else []
                else:
                    val[name] = desc if desc != 'null' else None

