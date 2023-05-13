.. _dev_setup:

*****************
Development Setup
*****************

To set up a development environment for this project, we recommend using a
virtual environment to ensure that your dependencies are isolated from other
projects on your system. The following instructions will guide you through
the process of setting up a virtual environment on Linux, Mac, and Windows.

.. warning::
    This documentation assumes familiarity with basic command line usage and
    some knowledge of virtual environments. If you are not comfortable with
    these concepts, please refer to the relevant documentation before
    proceeding.


1. Clone the main Git reppository via command line:

    .. code-block:: bash
        :caption: All platforms

        git clone https://github.com/MAST-Framework/MAST-F.git && cd MAST-F

2. Run the following command to create a new virtual environment:

    .. code-block:: bash
        :caption: On Linux and Mac:

        python3 -m venv ./venv

    .. code-block:: console
        :caption: On Windows

        py -m venv .\venv

3. Activate the virtual environment by running the appropriate command for your system:

    .. code-block:: bash
        :caption: On Linux and Mac:

        source ./venv/bin/activate


    .. code-block:: console
        :caption: Windows

        .\venv\Scripts\activate

4. Once your virtual environment is active, install the required packages by running the following command:

    .. code-block:: bash

        pip install .r requirements.txt

    .. note::
        The ``requirements.txt`` file contains a list of all packages required to
        run the development server. You can modify this file to add or remove packages
        as needed.


You now have a fully functional development environment for this project. You can start the development server
pointing to ``localhost:8000`` with the following command:

.. code-block:: bash
    :caption: On Linux and Mac

    python3 manage.py runserver

.. code-block:: bash
    :caption: On Windows

    py manage.py runserver

