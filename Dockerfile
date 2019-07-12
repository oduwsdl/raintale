ARG     PYTAG=3.7.3-stretch
FROM    python:${PYTAG}

LABEL   app.name="Raintale" \
        app.description="A Python utility and library for publishing a social media story built from archived web pages to multiple services" \
        app.license="MIT License" \
        app.license.url="https://github.com/oduwsdl/raintale/blob/master/LICENSE" \
        app.repo.url="https://github.com/oduwsdl/raintale" \
        app.docs.url="https://raintale.readthedocs.io/en/latest/" \
        app.authors="Shawn M. Jones <https://github.com/shawnmjones>"

WORKDIR /app
COPY    . /app
RUN     pip install .
WORKDIR /raintale-work
