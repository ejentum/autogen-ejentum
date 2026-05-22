# Changelog

All notable changes to `autogen-ejentum` are documented here. This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-23

### Added

- Initial release.
- `ejentum_tools(api_key=None, api_url=..., timeout_seconds=10.0) -> list[Callable]` factory that returns four async tool closures (`harness_reasoning`, `harness_code`, `harness_anti_deception`, `harness_memory`) bound to a shared configuration via lexical scope.
- Each closure is an `async def` callable with a single `query: str` parameter and a Google-style docstring; AutoGen's `AssistantAgent` inspects the signature + docstring to generate the JSON schema the LLM sees.
- Async-native HTTP via `httpx.AsyncClient` (AutoGen is async-first; matching the host framework keeps tool calls non-blocking in `AssistantAgent`'s event loop).
- Construction-time and call-time validation: empty/whitespace query returns an actionable error without spending a paid API call. Missing `EJENTUM_API_KEY` returns an actionable error pointing to https://ejentum.com/pricing.
- Errors returned as human-readable strings for every failure path (no exceptions cross the tool boundary so an agent step never crashes the run).
- Unit tests cover the factory contract (returns 4 closures with correct `__name__`s, distinct docstrings, single-param signatures), the call helper failure surface (missing key, empty/whitespace/non-string query, invalid mode, 401, non-200, invalid JSON, unexpected shape, network error), and parametric per-mode dispatch via `respx` mock transport.
- Published to PyPI with OIDC trusted-publisher provenance attestation via GitHub Actions.

### Background

AutoGen (microsoft/autogen v0.4+) accepts a `tools=` list of either `autogen_core.tools.BaseTool` instances or plain async/sync callables on `AssistantAgent`. AutoGen handles schema generation from the callable's signature and docstring, so a `BaseTool` subclass adds boilerplate without adding capability for an API-key-based tool. This shim returns plain async callables; users who prefer the BaseTool wrapping can use `FunctionTool(callable)` from `autogen_core.tools` on the consumer side.
