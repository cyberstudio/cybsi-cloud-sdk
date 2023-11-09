FROM python:3.11.6-slim-bookworm

# gcc is for regex package build (regex is black dependency), see https://github.com/psf/black/issues/1112
# libffi-dev is for poetry.
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
    make

# install urllib v1.x manually to avoid 'strict' attribute error
RUN pip3 install "urllib3<2"
ARG POETRY_VERSION
RUN pip3 install poetry==${POETRY_VERSION}

WORKDIR /cybsi_cloud_sdk

# dependencies for poetry install
COPY poetry.lock pyproject.toml README.md ./
COPY ./cybsi/__version__.py ./cybsi/py.typed ./cybsi/

RUN poetry install --with docs

ADD . /cybsi_cloud_sdk
