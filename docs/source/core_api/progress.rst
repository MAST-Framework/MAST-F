.. _core_api_progress:

*****************
Progress Observer
*****************

The ``mastf.core.progress`` module provides functionality to observe and monitor the progress
of Celery tasks. It includes a class named :class:`Observer` that can be used to track the execution
and completion of Celery tasks. This documentation provides an overview of the Observer class
and its usage.

The :class:`Observer` class is designed to monitor the progress of Celery tasks and provide real-time
updates on their execution. It serves as a useful tool for tracking task progress, identifying potential
issues, and ensuring the successful completion of tasks. Some key features are:

1. Task Progress Tracking:

    The :class:`Observer` class allows you to monitor the progress of Celery tasks by tracking their state
    and providing updates during different stages of execution.

2. Real-Time Updates:

    It provides real-time updates on task progress, including information such as debug message, status, elapsed
    time, and completion percentage. These updates can be used to display progress indicators or log task progress
    in external systems.


Usage Example:
~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    from mastf.core.progress import Observer
    from celery import shared_task

    @shared_task(bind=True)
    def my_shared_task(self, *args):
        observer = Observer(self)

        # set the current completion percentage
        observer.pos = 34
        # otherwise specify it directly
        observer.update("Some information...", current=34)

        # Let the observer increment the position itself
        observer.update("Further information...", increment=True, step=5)

        if not some_condition:
            # Fail should be called on the end of a non-successful task
            _, meta = observer.fail("Test not passed")
            # always return a result as it will be used within the frontend
            return meta.get("description")

        try:
            so_something()
        except Exception as err:
            _, meta = observer.exception(err, "An error occurred!")
            return meta.get("description")

        # You can also return the updated metadata directly
        status, meta = observer.success("Finished task!")
        return meta


.. autoclass:: mastf.core.progress.Observer
    :members:

