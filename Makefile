# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

.PHONY: build re-build

IMAGE_NAME := tokman
CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)

build:
	$(CONTAINER_ENGINE) build -t $(IMAGE_NAME) .

re-build:
	$(CONTAINER_ENGINE) build --no-cache --pull-always -t $(IMAGE_NAME) .
