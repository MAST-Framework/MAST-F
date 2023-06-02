FROM python:3.10-slim-buster

# Ensures the python output i.e. the stdout and stderr streams are sent to
# terminal without being first buffered and that you can see the output of
# this application (e.g. django logs) in real time.
ENV PYTHONUNBUFFERED 1

# If this is set to a non-empty string, Python won’t try to write .pyc files
# on the import of source modules.
ENV PYTHONDONTWRITEBYTECODE 1

# Update the container and install all necessary dependencies
RUN apt-get update \
    # dependencies for building and installing Python packages
    && apt-get install -y build-essential \
    # postgresql dependencies - comment out if you don't use postgresql
    && apt-get install -y libpq-dev libssl-dev \
    # cleanup unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*


# Ensure all project dependencies are installed correctly
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt

COPY ./compose/local/django/entrypoint /django_entrypoint
# Note that we have to convert Windows line endings to UNIX line endings
RUN sed -i 's/\r$//g' /django_entrypoint
RUN chmod +x /django_entrypoint

# Copy and setup the web instance start script
COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# TODO: add file exclusion rules
COPY ./mastf /app/mastf
COPY ./yara /app/yara
COPY ./docs /app/docs
COPY ./manage.py /app
# COPY . /app

# Specify the working directory where we access our files at runtime
WORKDIR /app

ENTRYPOINT [ "/django_entrypoint" ]