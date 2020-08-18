# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

.PHONY: build re-build

IMAGE_NAME ?= tokman
WORKERS ?= 1
LOG_LEVEL ?= info
CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)
# The directory in which the private key is stored.
SECRETS_DIR ?= $(CURDIR)
TEST_TARGET := ./tests/
TESTING_CONFIG := $(CURDIR)/tests/data/testing_config.py

build:
	$(CONTAINER_ENGINE) build -f Containerfile -t $(IMAGE_NAME) .

re-build:
	$(CONTAINER_ENGINE) build --no-cache --pull=true -f Containerfile -t $(IMAGE_NAME) .

run:
	$(CONTAINER_ENGINE) run -it --rm -v $(CURDIR):/config:z -v $(SECRETS_DIR):/secrets:z --env TOKMAN_CONFIG=/config/config.py --env WORKERS=$(WORKERS) --env LOG_LEVEL=$(LOG_LEVEL) --publish 8000 tokman

check:
	find . -name "*.pyc" -exec rm {} \;
	TOKMAN_CONFIG=$(TESTING_CONFIG) PYTHONPATH=$(CURDIR) PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --verbose --showlocals  $(TEST_TARGET)
