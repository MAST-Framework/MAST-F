# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Simple module to parse Android Manifest files or XML files in general.

Use this package to react to specific XML nodes or their defined node
attributes. Besides the default Android XML nodes, user-defined nodes
can be visited as well.

The following example illustrates how to use a single :class:`AXmlVisitor`
to print out the application's name and all activities:

.. code-block:: python
    :linenos:

    from mastf.android import manifest

    visitor = manifest.AXmlVisitor()

    @visitor.manifest("android:name")
    def visit_name(element, name: str):
        print("Application Name:", name)

    @visitor.activity("android:name")
    def visit_activity(element, name: str):
        print("Found activity:", name)

    visitor.visit_document(xml)

"""
from xml.dom import minidom
from inspect import isclass

__all__ = ["AXmlVisitorBase", "AXmlVisitor"]


class _AXmlElement:
    """Internal class used to store handlers mapped to a
    specific attribute or node.

    Note that this class acts as a method decorator and
    should be used on methods that take the following
    arguments:

    - ``element``: The current minidom element
    - ``value``: The attribute's value or None if a node will be visited
    - ``*args``, ``**kwargs``: Additional arguments provided within the ``do_visit`` function of an ``AXmlVisitor``

    Example:

    >>> visitor = AXmlVisitor()
    # type(manifest) := _AXmlElement
    >>> @visitor.manifest("android:name")
    ... def visit_name(element, value):
    ...     pass
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.handlers = {}

    def __call__(self, attribute_name: str, *args, **kwds):
        def wrapper(func):
            if attribute_name in self:
                self[attribute_name].append(func)
            else:
                self[attribute_name] = func

            return func

        return wrapper

    def __getitem__(self, key) -> list:
        return self.handlers[key]

    def __setitem__(self, key, value):
        if isinstance(value, list):
            self.handlers[key] = value
        else:
            handlers = list(self.handlers[key]) if key in self else []
            handlers.append(value)
            self.handlers[key] = handlers

    def __contains__(self, key) -> bool:
        return key in self.handlers

    def __repr__(self) -> str:
        return f"<AXmlElement name=[{self.name}]>"

    def add(self, key: str, handler):
        """Adds a new handler to the given attribute or node name.

        This method call is equivalent to::

            obj["key"] = value

        :param key: attribute or node name
        :type key: str
        :param handler: callback function
        :type handler: ``Callable[None, [Element, str, *args]]``
        """
        self[key] = handler


class AXmlVisitorBase(type):
    """Base class for XMLVisitor classes.

    This class can be used on any declaring class that should store
    handler elements.

    >>> class MyVisitorClass(metaclass=AXmlVisitorBase):
    ...     class Meta:
    ...         nodes = [ 'manifest', 'uses-permission' ]

    The example above includes two XML attributes which can be called:

    >>> obj = MyVisitorClass()
    >>> @obj.manifest("android:name")
    ... def visit_manifest_name(element, value: str):
    ...     pass
    """

    def __new__(cls, name, bases, attrs: dict, **kwargs):
        super_new = super().__new__

        axml_elements = {}
        new_class = super_new(cls, name, bases, attrs, **kwargs)

        nodes = []
        exclude = []
        for key, value in attrs.items():
            if isinstance(value, _AXmlElement):
                axml_elements[key] = value

            elif key == "Meta" and isclass(value):
                obj = value()
                if hasattr(obj, "nodes"):
                    nodes = getattr(obj, "nodes")
                    assert isinstance(
                        nodes, (list, tuple)
                    ), "The 'nodes' attribute must be of type list or tuple"

                if hasattr(obj, "exclude"):
                    exclude = getattr(obj, "exclude")
                    assert isinstance(
                        exclude, (list, tuple)
                    ), "The 'exclude' attribute must be of type list or tuple"

        for element in nodes:
            if isinstance(element, str) and element not in exclude:
                nname = str(element).replace("-", "_")
                axml_elements[nname] = _AXmlElement(nname.lower())
                setattr(new_class, nname, axml_elements[nname])

        if hasattr(new_class, "__axml__"):
            # To add elements from super classes we check against
            # previously defined elements and add them accordingly.
            elements = getattr(new_class, "__axml__")
            for x in exclude:
                elements.pop(x)

            axml_elements.update(elements)

        setattr(new_class, "__axml__", axml_elements)
        return new_class


# Use this constant to get document attribute handlers
DOCUMENT = "doc"


class AXmlVisitor(metaclass=AXmlVisitorBase):
    """Implementation of a visitor-based XML reader.

    This class uses the features of the :class:`AXmlVisitorBase` to define
    nodes of the Android manifest.  The following code illustrates how
    to register handlers for attributes of specific XML nodes:

    >>> visitor = AXmlVisitor()
    >>> @visitor.uses_permission("android:name")
    ... def visit_permission_name(element, name: str):
    ...     pass

    Here, the function would be called when the attribute "android:name" on
    a ``uses-permission`` node has been detected.

    To register a handler for a specific XML node, use the ``start`` or
    ``end`` attribute. The callback method will be called wither before
    or after the element's attributes have been visted.

    >>> @visitor.start("uses-permission")
    >>> def visit_permission_node(element):
    ...     pass

    The call above is equivalent to the following (assume ``visit_permission_node``
    has been defined before):

    >>> visitor.manifest['uses-permission'] = visit_permission_node

    Note that the called function won't have any other positional arguments
    than the visited element. In addition, this class supports optional
    arguments that can be used within each handler:

    >>> visitor = AXmlVisitor(foo='bar')
    >>> @visitor.manifest('android:name')
    >>> def visit_name(element, value: str, foo: str):
    ...     pass

    .. important::
        Additional arguments must be present in all declared methods.
    """

    class Meta:
        nodes = [
            # Adds an action to an intent filter.
            "action",
            # Declares an activity component.
            "activity",
            # Declares an alias for an activity.
            "activity-alias",
            # The declaration of the application.
            "application",
            # Adds a category name to an intent filter.
            "category",
            # Specifies each screen configuration with which the application
            # is compatible.
            "compatible-screens",
            # Adds a data specification to an intent filter.
            "data",
            # Specifies the subsets of app data that the parent content provider
            # has permission to access.
            "grant-uri-permission",
            # Declares an Instrumentation class that enables you to monitor an
            # application's interaction with the system.
            "instrumentation",
            # Specifies the types of intents that an activity, service, or
            # broadcast receiver can respond to.
            "intent-filter",
            # The root element of the AndroidManifest.xml file.
            "manifest",
            # A name-value pair for an item of additional, arbitrary data that can
            # be supplied to the parent component.
            "meta-data",
            # Defines the path and required permissions for a specific subset of
            # data within a content provider.
            "path-permission",
            # Declares a security permission that can be used to limit access to
            # specific components or features of this or other applications.
            "permission",
            # Declares a name for a logical grouping of related permissions.
            "permission-group",
            # Declares the base name for a tree of permissions.
            "permission-tree",
            # Declares a content provider component.
            "provider",
            # Declares the set of other apps that your app intends to access.
            "queries",
            # Declares a broadcast receiver component.
            "receiver",
            # Declares a service component.
            "service",
            # Declares a single GL texture compression format that the app supports.
            "supports-gl-texture",
            # Declares the screen sizes your app supports and enables screen
            # compatibility mode for screens larger than what your app supports.
            "supports-screens",
            # Indicates specific input features the application requires.
            "uses-configuration",
            # Declares a single hardware or software feature that is used by the
            # application.
            "uses-feature",
            # Specifies a shared library that the application must be linked against.
            "uses-library",
            # Specifies a vendor-provided native shared library that the app must be
            # linked against.
            "uses-native-library",
            # Specifies a system permission that the user must grant in order for the
            # app to operate correctly.
            "uses-permission",
            # Specifies that an app wants a particular permission, but only if the app
            # is installed on a device running Android 6.0 (API level 23) or higher.
            "uses-permission-sdk-23",
            # Lets you express an application's compatibility with one or more versions
            # of the Android platform, by means of an API level integer.
            "uses-sdk",
            # Global document attributes
            "doc",
        ]

    start = _AXmlElement(None)
    """Stores handlers than would be called `before` the attributes of an element
    should be visited."""

    end = _AXmlElement(None)
    """Stores handlers than would be called `after` the attributes of an element
    should be visited."""

    def __init__(self) -> None:
        self.args = ()
        self.kwargs = {}

    def visit_document(self, document: minidom.Document, *args, **kwargs):
        """Reads the incoming document or parses a given buffer/string.

        :param document: the document to read
        :type document: minidom.Document | str | bytes
        """
        if isinstance(document, (str, bytes)):
            document = minidom.parseString(document)

        self.args = args or self.args
        self.kwargs = kwargs or self.kwargs

        self._visit_xml(self.start, document, DOCUMENT)
        self._visit_attributes(document, document.attributes, self.doc)
        for name in self.__axml__:
            for element in document.getElementsByTagName(name):
                self.visit_element(element)

        self._visit_xml(self.end, document, DOCUMENT)

    def visit_element(self, element: minidom.Element):
        """Visits a single XML element.

        :param element: the element to read
        :type element: minidom.Element
        """
        node_name = element.nodeName
        if node_name not in self.__axml__:
            return

        axml_element = self.__axml__[node_name]
        self._visit_xml(self.start, element, node_name)
        self._visit_attributes(element, element.attributes, axml_element)
        self._visit_xml(self.end, element, node_name)

    def _visit_xml(self, axml, element, node_name):
        if node_name in axml:
            for handler in axml[node_name]:
                handler(element, *self.args, **self.kwargs)

    def _visit_attributes(self, element, attrs: dict, axml_element: _AXmlElement):
        if not attrs:
            return

        for attr_name, attr_value in attrs.items():
            if attr_name in axml_element:
                for handler in axml_element[attr_name]:
                    handler(element, attr_value, *self.args, **self.kwargs)
