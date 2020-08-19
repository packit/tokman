# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

from datetime import timedelta, datetime
from flexmock import flexmock
from tokman import app
from tokman.app import AppNotInstalledError


def test_api_health(client):
    response = client.get("/api/health")
    assert "ok" in response.data.decode()


def test_get_access_token_existing(client, init_db):
    flexmock(app).should_call("get_token").never()
    response = client.get("/api/packit/ogr")
    assert "Token123" in response.data.decode()


def test_get_access_token_expired(client, init_db):
    flexmock(app).should_receive("get_token").and_return(
        "Token12345", datetime.utcnow() + timedelta(hours=1)
    ).once()
    response = client.get("/api/packit/packit")
    assert "Token12345" in response.data.decode()


def test_get_access_token_app_not_installed(client, init_db):
    flexmock(app).should_receive("get_token").and_raise(AppNotInstalledError)
    response = client.get("/api/packit/packit")
    assert response.status_code == 400
