FROM python:3.11.6-slim-bookworm

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /cybsi_cloud_sdk

# install docs dependencies
COPY ./docs/requirements.txt ./docs/requirements.txt
RUN pip3 install -r ./docs/requirements.txt

# install poetry dependencies
ARG POETRY_VERSION
RUN pip3 install poetry==${POETRY_VERSION}
COPY poetry.lock pyproject.toml README.md ./
COPY ./cybsi/__version__.py ./cybsi/py.typed ./cybsi/
RUN poetry install


ADD . /cybsi_cloud_sdk
