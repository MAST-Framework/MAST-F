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
    && apt-get install -y file git \
    # dependencies for building and installing Python packages
    && apt-get install -y build-essential \
    # postgresql dependencies - comment out if you don't use postgresql
    && apt-get install -y libpq-dev libssl-dev \
    # cleanup unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*


# Install Java
RUN apt-get update && apt-get install -y \
    default-jre-headless unzip wget

# Download and install Dex2jar
ENV DEX2JAR_VERSION="2.1"
RUN wget https://github.com/pxb1988/dex2jar/releases/download/v${DEX2JAR_VERSION}/dex2jar-${DEX2JAR_VERSION}.zip \
    && unzip dex2jar-${DEX2JAR_VERSION}.zip -d /opt \
    && chmod +x /opt/dex-tools-${DEX2JAR_VERSION}/d2j-* \
    && rm dex2jar-${DEX2JAR_VERSION}.zip



# Download and install Apktool
ENV APKTOOL_VERSION="2.5.0"
RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar -O /usr/local/bin/apktool.jar \
    && wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool \
    && chmod +x /usr/local/bin/apktool \
    && chmod +x /usr/local/bin/apktool.jar

ENV JADX_VERSION="1.4.7"
RUN wget -O jadx.zip https://github.com/skylot/jadx/releases/download/v${JADX_VERSION}/jadx-${JADX_VERSION}.zip \
    && unzip jadx.zip -d "/opt/jadx-${JADX_VERSION}" \
    && chmod +x "/opt/jadx-${JADX_VERSION}/bin/jadx" \
    && rm jadx.zip

# Set environment variables
ENV PATH="/opt/dex-tools-${DEX2JAR_VERSION}:/opt/jadx-${JADX_VERSION}/bin:${PATH}"

# Ensure all project dependencies are installed correctly
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt

COPY ./compose/local/django/entrypoint /django_entrypoint
# Note that we have to convert Windows line endings to UNIX line endings
RUN sed -i 's/\r$//g' /django_entrypoint
RUN chmod +x /django_entrypoint

# In order to apply this Dockerfile to our Celery worker and Celery beat
# containers, we have to setup their startup script:
COPY ./compose/local/django/celery/worker/start /start_celery_worker
RUN sed -i 's/\r$//g' /start_celery_worker
RUN chmod +x /start_celery_worker

COPY ./compose/local/django/celery/beat/start /start_celery_beat
RUN sed -i 's/\r$//g' /start_celery_beat
RUN chmod +x /start_celery_beat

# Setup semgrep rules for iOS and Android
RUN mkdir /semgrep
RUN pip install semgrep
RUN git clone https://github.com/mindedsecurity/semgrep-rules-android-security /semgrep/android \
    && cd /semgrep/android && git checkout ${ANDROID_SEMGREP_COMMIT_SHA}

# TODO: add file exclusion rules
COPY ./mastf /app/mastf
COPY ./yara /app/yara
COPY ./docs /app/docs
COPY ./manage.py /app

# Specify the working directory where we access our files at runtime
WORKDIR /app

ENTRYPOINT [ "/django_entrypoint" ]