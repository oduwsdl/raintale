FROM python:3.7.3-stretch

WORKDIR /app

COPY . /app

RUN pip install .

WORKDIR /raintale-work

