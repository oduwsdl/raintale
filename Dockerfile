FROM python:3.7.3-stretch

WORKDIR /app

COPY . /app

RUN pip install .

RUN mkdir /raintale-work

WORKDIR /raintale-work

# keep the container running so we can execute raintale commands
# CMD ["tail", "-f", "/dev/null"]
# CMD ["/bin/bash", "-l"]
ENTRYPOINT /bin/bash
