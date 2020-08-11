# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import os
from datetime import datetime
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from github import GithubIntegration

try:
    from flask_restx import Api, Resource
except ModuleNotFoundError:
    from flask_restplus import Api, Resource


api = Api()
db = SQLAlchemy()
github_integration = None


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/access_tokens.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    private_key = Path(os.getenv("GITHUB_PRIVATE_KEY")).read_text()
    app_id = int(os.getenv("GITHUB_APP_ID"))
    api.init_app(app)
    db.init_app(app)
    global github_integration
    github_integration = GithubIntegration(app_id, private_key)

    return app


class Token(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    namespace = db.Column(db.String(), unique=True, nullable=False)
    repository = db.Column(db.String(), unique=True, nullable=False)
    token = db.Column(db.String(), unique=True, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def is_expired(self):
        return (
            self.expires_at is None
            or self.token is None
            or (self.expires_at - datetime.utcnow()).seconds < 60
        )


def get_token(namespace, repository):
    inst_id = github_integration.get_installation(namespace, repository).id
    inst_id = inst_id if isinstance(inst_id, int) or inst_id is None else inst_id.value
    if not inst_id:
        raise RuntimeError(f"App is not installed on {namespace}/{repository}")
    inst_auth = github_integration.get_access_token(inst_id)
    # expires_at is UTC
    return inst_auth.token, inst_auth.expires_at


@api.route("/api/<string:namespace>/<string:repository>")
@api.param("namespace", "GitHub namespace")
@api.param("repository", "GitHub repository")
class AccessToken(Resource):
    def get(self, namespace: str, repository: str):
        """Return an access token for <namespace>/<repository>"""
        token = Token.query.filter_by(
            namespace=namespace, repository=repository
        ).first()
        if token is None:
            token = Token(namespace=namespace, repository=repository)
            db.session.add(token)

        if token.is_expired():
            token.token, token.expires_at = get_token(namespace, repository)

        db.session.commit()

        return {
            "repository": repository,
            "namespace": namespace,
            "access_token": token.token,
        }

        return f"Hello {namespace}/{repository}"
