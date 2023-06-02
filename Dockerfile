FROM python:3.7.12-slim-buster

ARG PIP_INDEX_URL

# gcc is for regex package build (regex is black dependency), see https://github.com/psf/black/issues/1112
# libffi-dev is for poetry.
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
    make

# install urllib v1.x manually to avoid 'strict' attribute error
RUN pip3 install "urllib3<2"
RUN pip3 install poetry==1.1.12

WORKDIR /cybsi_cloud_sdk

# dependencies for poetry install
COPY poetry.lock pyproject.toml ./
COPY ./cybsi/__version__.py ./cybsi/py.typed ./cybsi/

RUN poetry install

ADD . /cybsi_cloud_sdk
