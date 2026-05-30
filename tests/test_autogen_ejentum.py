"""Unit tests for autogen-ejentum."""

import inspect

import httpx
import pytest
import respx

from autogen_ejentum import ejentum_tools
from autogen_ejentum._api import call_logic_api


API_URL = "https://example.test/api/"


# Closure-index -> (Python __name__, on-wire mode string). AutoGen uses
# func.__name__ as the LLM-facing tool name; Python identifiers cannot
# contain hyphens, so closure symbols use underscores. The on-wire mode
# string sent in the POST body stays hyphenated.
INDEX_TO_NAME_AND_MODE = [
    (0, "reasoning", "reasoning"),
    (1, "code", "code"),
    (2, "anti_deception", "anti-deception"),
    (3, "memory", "memory"),
    (4, "adaptive_reasoning", "adaptive-reasoning"),
    (5, "adaptive_code", "adaptive-code"),
    (6, "adaptive_anti_deception", "adaptive-anti-deception"),
    (7, "adaptive_memory", "adaptive-memory"),
]


# ---------------------------------------------------------------------------
# Factory contract
# ---------------------------------------------------------------------------


def test_factory_returns_eight_async_callables():
    tools = ejentum_tools()
    assert len(tools) == 8
    for fn in tools:
        assert inspect.iscoroutinefunction(fn)


def test_factory_assigns_expected_function_names():
    tools = ejentum_tools()
    names = [fn.__name__ for fn in tools]
    expected = [name for _idx, name, _mode in INDEX_TO_NAME_AND_MODE]
    assert names == expected


def test_each_closure_has_google_style_docstring():
    tools = ejentum_tools()
    for fn in tools:
        assert fn.__doc__ is not None
        assert "Args:" in fn.__doc__, f"{fn.__name__} missing Args: section"
        assert "Returns:" in fn.__doc__, f"{fn.__name__} missing Returns: section"


def test_each_closure_takes_single_query_param():
    for fn in ejentum_tools():
        sig = inspect.signature(fn)
        params = list(sig.parameters)
        assert params == ["query"], f"{fn.__name__} must take exactly 'query', got {params}"


def test_factory_calls_are_independent_instances():
    a = ejentum_tools(api_key="key-a")
    b = ejentum_tools(api_key="key-b")
    # Different factory calls produce distinct closure objects (different lexical scopes)
    assert a[0] is not b[0]


# ---------------------------------------------------------------------------
# Per-tool mode dispatch via respx mock
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index,name,mode", INDEX_TO_NAME_AND_MODE)
@respx.mock
async def test_each_closure_dispatches_correct_mode(index, name, mode):
    route = respx.post(API_URL).mock(
        return_value=httpx.Response(
            200, json=[{mode: f"[PROCEDURE] sample {mode} injection"}]
        )
    )

    tools = ejentum_tools(api_key="test-key", api_url=API_URL)
    fn = tools[index]
    assert fn.__name__ == name

    query = (
        "I noticed drift. This might mean Y. Sharpen: Z."
        if "memory" in mode
        else "sample task"
    )
    result = await fn(query)

    assert f"sample {mode} injection" in result
    assert route.call_count == 1
    posted = route.calls.last.request
    body = posted.read().decode()
    assert f'"mode": "{mode}"' in body or f'"mode":"{mode}"' in body
    assert posted.headers["authorization"] == "Bearer test-key"


@respx.mock
async def test_explicit_api_key_overrides_env(monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "env-key")
    respx.post(API_URL).mock(
        return_value=httpx.Response(200, json=[{"reasoning": "injection"}])
    )

    tools = ejentum_tools(api_key="explicit-key", api_url=API_URL)
    await tools[0]("anything")

    posted = respx.calls.last.request
    assert posted.headers["authorization"] == "Bearer explicit-key"


@respx.mock
async def test_env_var_is_read_when_api_key_omitted(monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "env-key")
    respx.post(API_URL).mock(
        return_value=httpx.Response(200, json=[{"reasoning": "injection"}])
    )

    tools = ejentum_tools(api_url=API_URL)
    await tools[0]("anything")

    posted = respx.calls.last.request
    assert posted.headers["authorization"] == "Bearer env-key"


# ---------------------------------------------------------------------------
# call_logic_api: failure surface
# ---------------------------------------------------------------------------


async def test_empty_query_does_not_call_api(monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "test-key")
    with respx.mock() as r:
        result = await call_logic_api(
            mode="reasoning",
            query="",
            api_key=None,
            api_url=API_URL,
            timeout_seconds=10.0,
        )
    assert "query" in result.lower()
    assert "required" in result.lower()
    assert r.calls.call_count == 0


async def test_whitespace_query_does_not_call_api(monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "test-key")
    with respx.mock() as r:
        result = await call_logic_api(
            mode="reasoning",
            query="   \t\n  ",
            api_key=None,
            api_url=API_URL,
            timeout_seconds=10.0,
        )
    assert "query" in result.lower()
    assert r.calls.call_count == 0


async def test_non_string_query_does_not_call_api(monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "test-key")
    with respx.mock() as r:
        result = await call_logic_api(
            mode="reasoning",
            query=None,
            api_key=None,
            api_url=API_URL,
            timeout_seconds=10.0,
        )
    assert "query" in result.lower()
    assert r.calls.call_count == 0


async def test_invalid_mode_returns_validation_error():
    result = await call_logic_api(
        mode="not-a-mode",
        query="anything",
        api_key="test-key",
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "mode" in result.lower()
    assert "reasoning" in result.lower()


async def test_missing_api_key_returns_actionable_error(monkeypatch):
    monkeypatch.delenv("EJENTUM_API_KEY", raising=False)
    result = await call_logic_api(
        mode="reasoning",
        query="diagnose 503s under load",
        api_key=None,
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "EJENTUM_API_KEY" in result
    assert "ejentum.com/pricing" in result


@respx.mock
async def test_401_returns_actionable_error():
    respx.post(API_URL).mock(return_value=httpx.Response(401, text="Unauthorized"))
    result = await call_logic_api(
        mode="anti-deception",
        query="anything",
        api_key="bad-key",
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "401" in result
    assert "EJENTUM_API_KEY" in result


@respx.mock
async def test_non_200_returns_status_and_body():
    respx.post(API_URL).mock(return_value=httpx.Response(500, text="boom"))
    result = await call_logic_api(
        mode="code",
        query="anything",
        api_key="test-key",
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "500" in result
    assert "boom" in result


@respx.mock
async def test_invalid_json_response_is_handled():
    respx.post(API_URL).mock(
        return_value=httpx.Response(
            200,
            text="<html>not json</html>",
            headers={"Content-Type": "text/html"},
        )
    )
    result = await call_logic_api(
        mode="reasoning",
        query="anything",
        api_key="test-key",
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "not valid json" in result.lower()


@respx.mock
async def test_unexpected_response_shape_is_handled():
    respx.post(API_URL).mock(
        return_value=httpx.Response(200, json={"wrong": "shape"})
    )
    result = await call_logic_api(
        mode="code",
        query="anything",
        api_key="test-key",
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "unexpected response shape" in result.lower()


@respx.mock
async def test_non_string_injection_value_is_handled():
    respx.post(API_URL).mock(
        return_value=httpx.Response(
            200, json=[{"reasoning": ["not", "a", "string"]}]
        )
    )
    result = await call_logic_api(
        mode="reasoning",
        query="anything",
        api_key="test-key",
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "unexpected response shape" in result.lower()


@respx.mock
async def test_network_error_is_caught():
    respx.post(API_URL).mock(side_effect=httpx.ConnectError("simulated"))
    result = await call_logic_api(
        mode="memory",
        query="I noticed drift. This might mean Y. Sharpen: Z.",
        api_key="test-key",
        api_url=API_URL,
        timeout_seconds=10.0,
    )
    assert "network error" in result.lower()
    assert "simulated" in result
