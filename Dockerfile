ARG     PYTAG=3.7.3-stretch
FROM    python:${PYTAG}

LABEL   org.opencontainers.image.title="Raintale" \
        org.opencontainers.image.description="A Python utility and library for publishing a social media story built from archived web pages to multiple services" \
        org.opencontainers.image.licenses="MIT License" \
        org.opencontainers.image.source="https://github.com/oduwsdl/raintale" \
        org.opencontainers.image.documentation="https://raintale.readthedocs.io/" \
        org.opencontainers.image.vendor="Web Science and Digital Libraries Research Group at Old Dominion University" \
        org.opencontainers.image.authors="Shawn M. Jones <https://github.com/shawnmjones>"

WORKDIR /app
COPY    . ./
RUN     pip install .

WORKDIR /raintale-work
