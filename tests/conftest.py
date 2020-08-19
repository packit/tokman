# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import pytest

from datetime import datetime, timedelta
from tokman import create_app
from tokman.app import db, Token


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture
def init_db():
    db.create_all()

    token1 = Token(
        repo="packit/ogr",
        token="Token123",
        expires_at=datetime.utcnow() + timedelta(minutes=20),
    )
    token2 = Token(
        repo="packit/packit",
        token="Token-will-expire",
        expires_at=datetime.utcnow() + timedelta(seconds=50),
    )
    db.session.add(token1)
    db.session.add(token2)

    db.session.commit()

    yield db

    db.drop_all()
