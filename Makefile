# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

.PHONY: build-image rebuild build-test-image rebuild-test-image

IMAGE_NAME ?= tokman
TEST_IMAGE ?= tokman-test
WORKERS ?= 1
LOG_LEVEL ?= info
CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)
# The directory in which the private key is stored.
SECRETS_DIR ?= $(CURDIR)
TEST_TARGET := ./tests/
TESTING_CONFIG := $(CURDIR)/tests/data/testing_config.py

build:
	$(CONTAINER_ENGINE) build -f Containerfile -t $(IMAGE_NAME) .

rebuild:
	$(CONTAINER_ENGINE) build --no-cache --pull=true -f Containerfile -t $(IMAGE_NAME) .

run:
	$(CONTAINER_ENGINE) run -it --rm \
		-v $(CURDIR):/config:z \
		-v $(SECRETS_DIR):/secrets:z \
		-v $(CURDIR):/access_tokens:z \
		--env TOKMAN_CONFIG=/config/config.py \
		--env WORKERS=$(WORKERS) \
		--env LOG_LEVEL=$(LOG_LEVEL) \
		--network=host \
		$(IMAGE_NAME)

build-test-image: build
	$(CONTAINER_ENGINE) build -f Containerfile.tests -t $(TEST_IMAGE) .

rebuild-test-image: rebuild
	$(CONTAINER_ENGINE) build --no-cache -f Containerfile.tests -t $(TEST_IMAGE) .

check:
	find . -name "*.pyc" -exec rm {} \;
	TOKMAN_CONFIG=$(TESTING_CONFIG) PYTHONPATH=$(CURDIR) PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --verbose --showlocals  $(TEST_TARGET)

check-in-container:
	$(CONTAINER_ENGINE) run --rm -it -v $(CURDIR):/src:Z -w /src $(TEST_IMAGE) make check
