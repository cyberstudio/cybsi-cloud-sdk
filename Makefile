ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DOCS_DIR := ${ROOT_DIR}/docs
DOCKER_FLAGS ?= --rm=true
DOCKER_BUILD_FLAGS ?= --force-rm=true --pull --rm=true
DOCKER_IMAGE := cybsi/cybsi-cloud-sdk
DOCKER_TAG ?= latest
VENV_DIR ?= .venv
SOURCE_DIRS := cybsi examples # TODO: add tests
POETRY_VERSION := 1.7.0

# If the first argument is "bump-version"...
ifeq (bump-version,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "bump-version"
  NEW_VERSION := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(NEW_VERSION):;@:)
endif

.PHONY: lint
lint:
	poetry run black $(SOURCE_DIRS)
	poetry run flake8 $(SOURCE_DIRS)
	poetry run mypy $(SOURCE_DIRS)
	poetry run isort $(SOURCE_DIRS)

.PHONY: test
test:
	#poetry run pytest --tb=native --verbose ./tests/

.PHONY: build-docs
build-docs:
	make -C ${DOCS_DIR} linkcheck html

.PHONY: image-build
image-build:
	docker build $(DOCKER_BUILD_FLAGS) --build-arg POETRY_VERSION=${POETRY_VERSION} --tag "$(DOCKER_IMAGE):$(DOCKER_TAG)" "$(ROOT_DIR)"

.PHONY: image-clean
image-clean: ### Remove last version of the images.
	docker rmi -f "$$(docker images -q $(DOCKER_IMAGE):$(DOCKER_TAG))"

.PHONY: docker-lint
docker-lint:
	docker run $(DOCKER_FLAGS) "$(DOCKER_IMAGE):$(DOCKER_TAG)" \
		make lint

.PHONY: docker-test
docker-test:
	docker run $(DOCKER_FLAGS) "$(DOCKER_IMAGE):$(DOCKER_TAG)" \
		make test

.PHONY: docker-build-docs
docker-build-docs:
	mkdir -p docs/_build
	docker run -iv ${PWD}:/cybsi/ $(DOCKER_FLAGS) "$(DOCKER_IMAGE):$(DOCKER_TAG)" \
		sh -c "trap \"chown -R $$(id -u):$$(id -g) /cybsi/docs/_build\" EXIT; BUILDDIR=/cybsi/docs/_build make build-docs"

.PHONY: docker-clean
docker-clean:
	docker rmi -f "$$(docker images -q $(DOCKER_IMAGE):$(DOCKER_TAG))"

################ Helper targets ################
.PHONY: tools
tools: #### Install tools needed for development.
	pip3 install poetry==${POETRY_VERSION}
	poetry install

.PHONY: docs-tools
docs-tools: #### Install tools needed for documentation development.
	pip3 install -r ${DOCS_DIR}/requirements.txt
	pip3 install pip-tools

.PHONY: update-docs-dependencies
update-docs-dependencies: #### Update pinned docs dependencies.
	make -C ${DOCS_DIR} update-requirements


.PHONY: bump-version
bump-version:
	poetry run tbump --no-push --no-tag $(NEW_VERSION)
