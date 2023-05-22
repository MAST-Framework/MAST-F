.. _intro_docker_setup:

*************************
Setup with Docker Compose
*************************

This project uses Docker Compose to manage its container environment. With Docker Compose, you
can easily set up and run all the required services and dependencies for this project with a
single command.

The following figure illustrates how the default costellation of muliple containers is meant to
be reviewed. The compose file is named ``docker-compose.local.yml`` and all relevant configuration
files are located in the ``/compose/local/`` directory.

.. figure:: images/container-view.svg
    :alt: Overview of container architecture

    Figure 1: Overview of container architecture. Note that our Django container will be able to
    comunicate with containers in the backend network. Note also that the storage network is still
    under development and can't be integrated yet.



=================
Local Development
=================

To get started **locally**, follow these steps:

1. Ensure that you have Docker and Docker Compose installed on your machine. If you do not have them installed, please refer to the official Docker documentation for installation instructions at `Docker.com <https://www.docker.com/>`_.
2. Open the ``docker-compose.yml`` file in the root directory of the project to review the available services and their configuration.
3. Generate a self signed certificate and private key to enable HTTPS. Save the generated files to ``/compose/local/nginx/``:

    .. code-block:: bash
        :caption: On Linux and Mac

        openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365

    .. note::
        If you have Git installed on your Windows system, open Git Bash, navigate to the
        project's directory and execute the command above.

4. Run the following command to start all the required services and dependencies:

    .. code:: bash

        docker compose up -d

    .. note::
        The first time you run this command, Docker Compose will build the required images
        for your services, which may take some time depending on your internet speed and
        system resources. Subsequent runs will use the pre-built images.

5. Once the services are running, you can access your application by navigating to https://localhost:<port> in your web browser, where <port> is the port number specified in the docker-compose.yml file (default ``8443``).

    .. warning::
        If the port you specified in the docker-compose.yml file is already in use by
        another application on your machine, you may need to change it to a different
        port number.

You now have a fully functional development environment for this project, powered by Docker
Compose. Before setting up a production environment, consider reading the following sections
which address different configuration options.

=====================
Service Configuration
=====================


Database
--------

As per default, there is a container named ``backend-db`` which is basically a PostgreSQL server
within the backend Docker network. The following code snippet shows what configurations should
be applied to the service:

.. code-block:: yaml
    :linenos:
    :lineno-start: 40

    backend-db:
        image: postgres:13.0-alpine
        volumes:
            # The target data volume (may be a shared directory)
            - postgres_data:/var/lib/postgresql/data/
        environment:
            # Specify environment variables here or place them in an
            # environment file. Make sure to keep the password private
            # in production environments!
            - POSTGRES_USER=mastf_django
            - POSTGRES_PASSWORD=supersecretpassword
            - POSTGRES_DB=mastf_backend_db
        networks:
            - backend

- ``POSTGRES_USER=mastf_django``:
    Sets the username of the default PostgreSQL user that will be used by the application. The value of this
    variable is set to *mastf_django*, which is the default user used by the django application.

- ``POSTGRES_PASSWORD=supersecretpassword``:
    This configuration variable sets the password for the default PostgreSQL user that will be used by the
    application. The default value is set to *supersecretpassword*, which is a strong password that should
    be replaced with a unique and secure password before deploying the application.

- ``POSTGRES_DB=mastf_backend_db``:
    Sets the name of the default PostgreSQL database that will be used by the application. The value of this
    variable is set to ``mastf_backend_db``, which is the name of the default database used by the django
    backend application.

Note that these configuration variables are used to set up the PostgreSQL database for the django application.
It is important to keep these configuration variables secure and not share them with unauthorized users.
Additionally, it is recommended to replace the default values of these configuration variables with unique and
secure values before deploying the project.

.. note::
    The environment variables ``POSTGRES_USER`` and ``POSTGRES_DB`` must point to the same value
    as ``DB_USER`` and ``DB_NAME`` do defined in your environment file.

    By default, the following section of the configuration file describes how to place the mentioned environment
    variables:

    .. code-block:: properties

        # Specify user and password only once
        DB_DATABASE=mastf_backend_db
        DB_USER=mastf_django
        DB_PASSWORD=supersecretpassword

        POSTGRES_USER=${DB_USER}
        POSTGRES_PASSWORD=${DB_PASSWORD}
        POSTGRES_DB=${DB_DATABASE}

Broker
------

We use a `Redis <https://redis.io/>`_ service instance as our message broker and result backend. Configuration variables
used wihtin the django application should be set in the environment file of this project:

- ``CELERY_BROKER_URL = "redis://redis:6379/0"``:
    This environment variable sets the URL of the Redis instance that will be used as the broker for Celery tasks. The value
    of this variable is set to ``redis://redis:6379/0``, which indicates that the Redis instance is running on the same Docker
    network as the Celery worker container and that it is accessible at the address ``redis:6379``. The ``/0`` at the end of
    the URL specifies the Redis database that will be used for Celery tasks.

- ``CELERY_RESULT_BACKEND="redis://redis:6379/0"``:
    This environment variable sets the URL of the Redis instance that will be used as the backend for storing Celery task
    results. The value of this variable is also set to ``redis://redis:6379/0``, which indicates that the same Redis instance that
    is used as the broker will also be used as the backend for storing task results.



Nginx
-----

The Nginx reverse proxy is a powerful tool for directing incoming network traffic to backend servers. This chapter provides a
detailed guide on configuring the Nginx service using the available configuration variables. It also includes recommendations
for accepting only HTTPS traffic and generating a self-signed certificate and private key for the Nginx server.

Configuration Steps
~~~~~~~~~~~~~~~~~~~

1. Install Nginx:
    Ensure that Nginx is installed on your server or local machine if you don't want to use docker. Otherwise, take a quick look
    at the pre-defined docker-compose configuration

    .. code-block:: yaml

        nginx:
            # build context with configuration files
            build: ./compose/local/nginx/
            env_file:
                # environment variables
                - ./.env/.dev-example
            ports:
                - ${NGINX_HTTP_PORT}:80
                - ${NGINX_HTTPS_PORT}:443
            environment:
                NGINX_ENVSUBST_TEMPLATE_SUFFIX: ".conf"
            depends_on:
                - web-django
            networks:
                - frontend

2. Nginx Configuration File:
    There are two pre-defined nginx configuration files: one for HTTP-only servers and one for strict HTTPS servers. Note that
    there will be only HTTPS-traffic allowed with the default configuration (recommended).

    .. hint::
        You can use environment variables declared in your environment file ``./.env/.dev-example`` in the Nginx configuration
        file:

        .. code-block:: nginx

            upstream django {
                server web-django:${DJANGO_PORT};
            }

    However, if you want to enforce HTTP traffic, you have to apply the following changes to the Dockerfile placed in
    ``compose/nginx``:

    .. code-block:: dockerfile

        # Instead of preparing SSL (remove the following directives)
        COPY default.conf.conf /etc/nginx/templates/default.conf.conf
        RUN mkdir -p /etc/ssl/
        COPY cert.pem /etc/ssl/cert.pem
        COPY key.pem /etc/ssl/key.pem

        # Just copy the HTTP configuration (add thid line)
        COPY nginx.http.conf /etc/nginx/conf.d/default.conf

3. Generate Self-Signed Certificate

    .. note::
        Ensure that OpenSSL is installed on your system. Use the package manager or download it from the official website.
        For Windows users: If you have git installed on your system, make sure that you have also installed Git Bash. Run
        Git Bash in order to start a new window with a bash shell in it. You can now execute the command described below.

    In a new terminal, run the following commands to generate a self-signed certificate and private key:

    .. code:: bash

        openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout /path/to/key.pem -out /path/to/cert.pem

    In order to use the generated private key and certificate, copy them into the ``compose/nginx/`` directory of this
    repository.


.. caution::
    These steps provide a simplistic overview of how HTTPS can be enabled via a nginx reverse proxy. It is not meant to be
    complete in any ways. For more HTTPS security related information, please refer to the `NGINX Guide <https://www.nginx.com/resources/wiki/start/topics/examples/full/>`_.


Environment Options
~~~~~~~~~~~~~~~~~~~

- ``NGINX_HTTP_PORT=8080``:
    This configuration variable specifies the port number on which the Nginx server listens for incoming HTTP
    connections. The default value is set to ``8080``, but it can be modified to any available port number.

    * Any HTTP traffic received on this port will be directed to the backend servers configured in the Nginx reverse proxy.

- ``NGINX_HTTPS_PORT=8443``:
    This configuration variable defines the port number on which the Nginx server listens for incoming HTTPS
    connections. The default value is set to ``8443``, but it can be changed to any available port number.

    * HTTPS traffic received on this port will be securely handled by the Nginx server using SSL/TLS encryption.
    * It is important to configure the Nginx server with a valid SSL/TLS certificate and private key to enable HTTPS communication on this port.
    * Typically, the backend servers behind the Nginx reverse proxy will communicate over plain HTTP, while the Nginx server itself handles the SSL/TLS encryption for incoming HTTPS requests.



Django
------

The following environment variables apply to all services using the environment file. For frontend specific configurations,
please refer to the :doc:`Django Settings` documentation.

.. note::
    All described environment variables cannot be used in local development.

.. py:data:: DJANGO_DEBUG
    :value: 1
    :type: int

    Control whether the web instance should be running in debug mode to provide detailed exception descriptions.

    .. warning::
        Never enable this option in production environments as it would potentially leak important and sensitive
        configuration vairables.

.. py:data:: DJANGO_SECRET_KEY
    :type: str

    Specifies the secret key that Django will use. For more information about secret keys in Django, please refer to the
    chapter `Cryptographic signing <https://docs.djangoproject.com/en/4.2/topics/signing/>`_ of the Django documentation.

.. py:data:: DJANGO_ALLOWED_HOSTS
    :type: str
    :value: "*"

    Make sure to edit the allowed host variable to specify which host should be able to connect to your web instance. Sperate
    them with ``:`` to add multiple hosts.

.. py:data:: DJANGO_CSRF_TRUSTED_ORIGINS
    :type: str
    :value: "https://localhost:8443|https://127.0.0.1:8443"

    Trusted origins when configuring Django to run with HTTPS.

    .. important::
        Configure the trusted hosts if you are using a reverse proxy like nginx. Replace hostnames of the given URLs to match
        your own ones.

.. py:data:: DJANGO_SESSION_EXPIRE_AT_BROWSER_CLOSE
    :type: int
    :value: 1

    Use this configuration to control whether django should remove active sessions when the browser is closed.

.. py:data:: DJANGO_SESSION_COOKIE_AGE
    :type: int
    :value: 3600

    Control the TTL of a session cookie default will be 3600s = 1h

.. py:data:: DJANGO_HTTPS
    :type: bool
    :value: True

    Control whether you want to start your services with HTTPS enabled. Enable this option only if you want
    to use HTTPS.

.. py:data:: DJANGO_STORAGE_URL
    :type: str
    :value: "/app_storage/"

    The storage URL where all project data should be saved separately. Note the trailing ``/`` that is needed
    by Django. Remove this connfiguration if you work locally.


.. py:data:: DJANGO_STORAGE_ROOT
    :type: str
    :value: "/app_storage"

    Same as described in :data:`DJANGO_STORAGE_URL` without traling slash.

.. py:data:: DJANGO_PORT
    :type: int
    :value: 8000

    The port django should be served on.


