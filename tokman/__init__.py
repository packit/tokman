# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

from flask import request

from .app import create_app

application = create_app()


@application.before_request
def before_request():
    application.logger.debug(
        "remote: %s:%s %s",
        request.environ.get("REMOTE_ADDR", ""),
        request.environ.get("REMOTE_PORT", ""),
        request.environ.get("HTTP_USER_AGENT", ""),
    )


@application.after_request
def after_request(response):
    application.logger.debug("response status: %s", response.status)
    return response
