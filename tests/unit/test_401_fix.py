# tests/unit/test_401_fix.py
"""Regression tests for 401 handling in GraphDefinitionRunner.execute_query.

A 401 used to fall through to the generic ``else`` branch, which silently set
``retry = max_retry`` and returned an empty list -- masking an expired/missing
credential as "no results". It should instead raise a clear RuntimeError that
tells the user to re-authenticate.
"""

import asyncio

import pytest
from pytest_httpx import HTTPXMock

from fhir_aggregator_client import GraphDefinitionRunner


def test_401_raises_runtime_error(httpx_mock: HTTPXMock) -> None:
    """A 401 should raise a clear RuntimeError, not silently return []."""
    url = "http://testserver/Patient?_id=123"
    httpx_mock.add_response(url=url, status_code=401, json={"error": "unauthorized"})

    runner = GraphDefinitionRunner(fhir_base_url="http://testserver")

    with pytest.raises(RuntimeError) as exc_info:
        asyncio.run(runner.execute_query(url))

    msg = str(exc_info.value)
    assert "401" in msg
    assert "gcloud auth application-default login" in msg


def test_401_does_not_retry(httpx_mock: HTTPXMock) -> None:
    """The 401 path must fail fast -- exactly one request, no retry loop."""
    url = "http://testserver/Patient?_id=123"
    httpx_mock.add_response(url=url, status_code=401, json={"error": "unauthorized"})

    runner = GraphDefinitionRunner(fhir_base_url="http://testserver")

    with pytest.raises(RuntimeError):
        asyncio.run(runner.execute_query(url))

    # If execute_query had retried, pytest_httpx would report extra unmatched
    # requests (only one response is registered).
    assert len(httpx_mock.get_requests()) == 1


def test_non_auth_http_error_returns_empty(httpx_mock: HTTPXMock) -> None:
    """A non-retryable, non-auth status (e.g. 500) keeps the old behavior: no
    raise, returns an empty list after abandoning the query."""
    url = "http://testserver/Patient?_id=123"
    httpx_mock.add_response(url=url, status_code=500, json={"error": "boom"})

    runner = GraphDefinitionRunner(fhir_base_url="http://testserver")

    result = asyncio.run(runner.execute_query(url))
    assert result == []
