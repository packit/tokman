# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

.PHONY: build re-build

IMAGE_NAME := tokman
CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)
# The directory in which the private key is stored.
SECRETS_DIR ?= $(CURDIR)

build:
	$(CONTAINER_ENGINE) build -f Containerfile -t $(IMAGE_NAME) .

re-build:
	$(CONTAINER_ENGINE) build --no-cache --pull=true -f Containerfile -t $(IMAGE_NAME) .

run:
	$(CONTAINER_ENGINE) run -it --rm -v $(CURDIR):/config:z -v $(SECRETS_DIR):/secrets:z --env TOKMAN_CONFIG=/config/config.py --publish 8000 tokman
