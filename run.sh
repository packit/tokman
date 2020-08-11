#!/usr/bin/bash

# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

set -eux

alembic-3 upgrade head
sleep 1
gunicorn -w ${WORKERS:-1} --log-level ${LOG_LEVEL:-info} tokman
