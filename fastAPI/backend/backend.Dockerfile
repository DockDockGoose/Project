# pull official base image
FROM python:3.9.2-slim-buster

# Pull tiangolo configured image
# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# set working directory
WORKDIR /app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install curl \
  && apt-get -y install netcat gcc \
  && apt-get clean

# install python dependency manager - upgrade pip first
RUN pip install --upgrade pip
# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false


# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

# add app
COPY ./app /app
ENV PYTHONPATH=/app

# Install python dependencies
RUN poetry install --no-interaction --no-ansi

RUN chmod +x entrypoint.sh
ENTRYPOINT ["bash", "entrypoint.sh"]