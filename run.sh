#!/usr/bin/bash

set -eux

alembic upgrade head
sleep 1
gunicorn -w ${WORKERS:-1} --log-level debug tokman
