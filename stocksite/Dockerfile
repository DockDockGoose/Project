FROM python:3

ENV PYTHONUNBUFFERED=1
RUN mkdir /mongodb
WORKDIR /mongodb
COPY requirements.txt /mongodb/
RUN pip install -r requirements.txt
COPY . /mongodb/