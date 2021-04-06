# pull official base image
FROM python:3

# create & set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.dev.txt /code/
RUN pip3 install -r requirements.dev.txt
RUN apt-get update \
    && apt-get install -yyq netcat

# copy entrypoint.sh
COPY ./entrypoint.sh /code/entrypoint.sh
# provide executable permissions to entrypoint script
RUN chmod +x /code/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
# ENTRYPOINT ["sh", "entrypoint.sh"]