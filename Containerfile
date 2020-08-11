# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

FROM fedora:32

RUN dnf install -y \
    python3-flask \
    python3-flask-restx \
    python3-alembic \
    python3-flask-sqlalchemy \
    python3-pygithub \
    python3-gunicorn \
    && dnf clean all

WORKDIR /tokman
COPY run.sh run.sh

CMD ["run.sh"]
