# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

try:
    from flask_restx import Api, Resource
except ModuleNotFoundError:
    from flask_restplus import Api, Resource

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/access_tokens.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)
db = SQLAlchemy(app)


class Token(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    namespace = db.Column(db.String(), unique=True, nullable=False)
    repository = db.Column(db.String(), unique=True, nullable=False)
    token = db.Column(db.String(), unique=True, nullable=True)
    expires = db.Column(db.DateTime, nullable=True)

    def is_expired(self):
        return (
            self.expires is None
            or self.token is None
            or (self.expires - datetime.utcnow()).seconds < 60
        )


def get_token(namespace, repository):
    return "dummy", datetime.utcnow()


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
            token.token, token.expires = get_token(namespace, repository)

        db.session.commit()

        return {
            "repository": repository,
            "namespace": namespace,
            "access_token": token.token,
        }

        return f"Hello {namespace}/{repository}"


if __name__ == "__main__":
    app.run(debug=True)
