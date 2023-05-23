.. _api_forms:

**************
Enhanced Forms
**************

.. automodule:: mastf.MASTF.forms

To get started with the new form fields we've just introduced, let's create a
new form class that will define the fields we want to receive from the client.
Here's an example:

.. code-block:: python
    :linenos:

    from django import forms
    from mastf.MASTF.forms import ModelField
    from .models import MyModel

    class SampleForm(forms.Form):
        field1 = ModelField(MyModel, mapper=int)
        field2 = forms.CharField(...)

In this example, we create a new form class called ``SampleForm`` that inherits
from ``forms.Form``. we define a :class:`ModelField` that will use an incoming integer
value as the primary key search value.

.. note::
    Values of :class:`ModelField` and :class:`ManyToManyField` fields should be transmitted
    as string values as these fields expect a string as input. You can define a *mapper*
    function to convert an input string into your preferred primary key value.

---------------
Enhanced Fields
---------------

.. autoclass:: mastf.MASTF.forms.ModelField
    :members:

.. autoclass:: mastf.MASTF.forms.ManyToManyField
    :members: