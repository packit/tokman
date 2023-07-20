# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

FROM quay.io/packit/base:c9s

WORKDIR /tokman

# 1. line: tokman deps from setup.cfg (Add python-flask-sqlalchemy once it's in epel9 (RHBZ#2169000))
# 2. line: packages needed to run it
# 3. line: sentry-sdk dependencies
RUN dnf install -y --setopt=install_weak_deps=False \
    python3-flask-restx python3-pygithub python3-cryptography \
    git python3-gunicorn python3-alembic sqlite \
    python3-blinker python3-certifi \
    && dnf clean all

COPY . /tokman/

# - The above python3-pygithub RPM installs python3-requests-2.25.1 and python3-urllib3-1.26.5
#   The sentry_sdk would then install urllib3-2.x because of its urllib3>=1.26.11 requirement
#   and 'pip check' would then scream that "requests 2.25.1 has requirement urllib3<1.27"
# - flask-sqlalchemy-3 requires flask>2.2 and we have flask-2.0.3 in epel9
RUN pip install sentry-sdk[flask] \
    'urllib3<1.27' \
    'flask-sqlalchemy<3' \
    . \
    && pip check

EXPOSE 8000
VOLUME /secrets

CMD ["./run.sh"]
