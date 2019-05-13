FROM python:3.7.3-stretch

WORKDIR /app

COPY . /app

RUN pip install .

WORKDIR /raintale-work

# keep the container running so we can execute raintale commands
ENTRYPOINT /bin/bash
