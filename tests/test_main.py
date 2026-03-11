"""Tests for the list-gists API. All GitHub calls are mocked."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from gist_api.main import app
from tests.conftest import REQ, mock_github


# GET / returns health check message
def test_root(client):
    assert client.get("/").json() == {"message": "App is running.."}


# GitHub status codes (200, 404, 403) are forwarded as-is to the caller
@pytest.mark.parametrize("status", [200, 404, 403])
def test_status_forwarded(client, status):
    with mock_github(status=status):
        assert client.get("/octocat").status_code == status


# Timeout and connection failures return 502
@pytest.mark.parametrize("error", [httpx.ConnectTimeout("t"), httpx.ConnectError("e")])
def test_network_errors(client, error):
    with mock_github(error=error):
        assert client.get("/octocat").status_code == 502


# Valid usernames (alphanumeric, hyphens) pass; special characters get 422
@pytest.mark.parametrize("path,expected", [
    ("/valid-user", 200), ("/user123", 200), ("/bad user!", 422), ("/user.name", 422),
])
def test_username_validation(client, path, expected):
    with mock_github():
        assert client.get(path).status_code == expected


# Pagination defaults to page=1, per_page=30; custom values are forwarded to GitHub
@pytest.mark.parametrize("qs,page,per_page", [("", 1, 30), ("?page=2&per_page=50", 2, 50)])
def test_pagination(client, qs, page, per_page):
    mock_get = AsyncMock(return_value=httpx.Response(200, json=[], request=REQ))
    with patch.object(app.state.http, "get", new=mock_get):
        client.get(f"/octocat{qs}")
    mock_get.assert_called_once_with("/users/octocat/gists", params={"page": page, "per_page": per_page})


# Out-of-range pagination values (page<1, per_page<1 or >100) get 422
@pytest.mark.parametrize("qs", ["?page=0", "?page=-1", "?per_page=0", "?per_page=101"])
def test_invalid_pagination(client, qs):
    with mock_github():
        assert client.get(f"/octocat{qs}").status_code == 422
