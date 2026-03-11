"""Shared fixtures and helpers for gist-api tests."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from gist_api.main import app

REQ = httpx.Request("GET", "https://api.github.com")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def mock_github(status=200, json=None, error=None):
    side = {"side_effect": error} if error else {
        "return_value": httpx.Response(status, json=json or [], request=REQ)}
    return patch.object(app.state.http, "get", new=AsyncMock(**side))
