# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

FROM fedora:32

WORKDIR /tokman
ADD https://raw.githubusercontent.com/packit/deployment/master/scripts/setupcfg2rpm.py /tokman/setupcfg2rpm.py
COPY setup.cfg /tokman/

RUN dnf install -y \
    git \
    python3-gunicorn \
    python3-pip \
    sqlite \
    $(python3 setupcfg2rpm.py setup.cfg) \
    && dnf clean all

RUN pip install --upgrade sentry-sdk[flask]

COPY . /tokman/
RUN pip install --no-deps .

EXPOSE 8000
VOLUME /secrets

CMD ["./run.sh"]
