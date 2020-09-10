# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import logging
import os

from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from github import GithubIntegration

try:
    from flask_restx import Api, Resource
except ModuleNotFoundError:
    from flask_restplus import Api, Resource


api = Api()
db = SQLAlchemy()
github_integration = None
token_renew_at = None


def create_app():
    configure_sentry()
    app = Flask(__name__)
    app.config.from_envvar("TOKMAN_CONFIG")

    log_level = os.getenv("LOG_LEVEL", "info")
    log_level = getattr(logging, log_level.upper())
    logging.basicConfig(level=log_level)

    private_key = Path(app.config["GITHUB_APP_PRIVATE_KEY"]).read_text()
    app_id = int(app.config["GITHUB_APP_ID"])
    app.github_integration = GithubIntegration(app_id, private_key)

    api.init_app(app)
    db.init_app(app)

    return app


def configure_sentry() -> None:
    api.logger.debug("Setting up sentry for tokman.")

    secret_key = os.getenv("SENTRY_SECRET")
    if not secret_key:
        return

    # so that we don't have to have sentry sdk installed locally
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        secret_key,
        integrations=[FlaskIntegration(), SqlalchemyIntegration()],
        environment=os.getenv("DEPLOYMENT"),
    )
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("runner-type", "tokman")


class Token(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(db.String, unique=True, nullable=False)
    token = db.Column(db.String, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def is_expired(self):
        token_renew_at = timedelta(
            seconds=int(current_app.config.get("TOKEN_RENEW_AT", 60))
        )
        return (
            self.expires_at is None
            or self.token is None
            or (self.expires_at - datetime.utcnow()) < token_renew_at
        )


class AppNotInstalledError(Exception):
    pass


def get_token(namespace, repository):
    inst_id = current_app.github_integration.get_installation(namespace, repository).id
    inst_id = inst_id if isinstance(inst_id, int) or inst_id is None else inst_id.value
    if not inst_id:
        raise AppNotInstalledError(f"App is not installed on {namespace}/{repository}")
    inst_auth = current_app.github_integration.get_access_token(inst_id)
    # expires_at is UTC
    return inst_auth.token, inst_auth.expires_at


@api.route("/api/<string:namespace>/<string:repository>")
@api.param("namespace", "GitHub namespace")
@api.param("repository", "GitHub repository")
class AccessToken(Resource):
    def get(self, namespace: str, repository: str):
        """Return an access token for <namespace>/<repository>"""
        repo = f"{namespace}/{repository}"
        token = Token.query.filter_by(repo=repo).first()
        if token is None:
            api.logger.debug(f"Create {repo}")
            token = Token(repo=repo)
            db.session.add(token)

        if token.is_expired():
            try:
                api.logger.debug(f"Get token for {repo}")
                token.token, token.expires_at = get_token(namespace, repository)
            except AppNotInstalledError as err:
                api.logger.debug(f"Failed to get token for {repo}")
                return {"error": f"Failed to retrieve a token: {err}"}, 400

        db.session.commit()

        return {
            "repository": repository,
            "namespace": namespace,
            "access_token": token.token,
        }


@api.route("/api/health")
class Health(Resource):
    def get(self):
        """Is this up and running?"""
        return {"message": "ok"}

    def head(self):
        pass
