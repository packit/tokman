#!/usr/bin/bash

# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

set -eux

alembic-3 upgrade head
sleep 1
python3 -m gunicorn.app.wsgiapp -w ${WORKERS:-1} --log-level ${LOG_LEVEL:-info} --bind ${BIND_ADDR:-127.0.0.1:8000} tokman
