FROM python:3.12-slim

LABEL MAINTAINER="BigBagTM"

ARG APP_HOME="/opt/app"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_IGNORE_INSTALLED=true \
    PATH=/usr/bin/:${PATH} \
    PYTHONPATH={PYTHONPATH}:/opt/app/ \
    VIRTUAL_ENV=/opt/app/venv

WORKDIR ${APP_HOME}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        make \
        python3-pip \
        python3-virtualenv && \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/cache/apt/* \
            /var/lib/apt/* \
            ~/.cache/pip/* \
            /tmp/* \
            /var/tmp/*

COPY pyproject.toml uv.lock Makefile ./

RUN make venv/create && \
    make venv/install/main && \
    rm -rf ~/.cache/pypoetry ~/.cache/uv ~/.cache/pip

COPY src/ src/
