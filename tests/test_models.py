# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import pytest

from datetime import datetime, timedelta
from tokman.app import Token


@pytest.mark.parametrize(
    "token, is_expired",
    (
        (Token(expires_at=None, token=None), True),
        (Token(expires_at=None, token="Token123"), True),
        (Token(expires_at=datetime.utcnow() + timedelta(minutes=10), token=None), True),
        (
            Token(
                expires_at=datetime.utcnow() + timedelta(minutes=10), token="Token123",
            ),
            False,
        ),
        (
            Token(
                expires_at=datetime.utcnow() + timedelta(seconds=10), token="Token123",
            ),
            True,
        ),
    ),
)
def test_is_expired(token, is_expired, app):
    assert token.is_expired() == is_expired
