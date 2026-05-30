# autogen-ejentum

[AutoGen](https://microsoft.github.io/autogen/) tools for the Ejentum Reasoning Harness. `ejentum_tools()` returns eight async tool closures bound to a shared config that AutoGen's `AssistantAgent` calls before generating.

Use the harness before the agent generates on complex, multi-step, or multi-constraint tasks where the model's default reasoning template would miss a constraint, take a shortcut, or drift across turns. Each call returns a *cognitive operation*: a structured procedure (numbered steps with a failure pattern to refuse and a falsification test) paired with an executable reasoning topology (a DAG of those steps with decision gates, parallel branches, bounded loops, and meta-cognitive exit nodes). The agent reads both layers before producing its response.

Four dynamic closures (`reasoning`, `code`, `anti_deception`, `memory`) are available on all tiers including the 30-day free trial. Four adaptive closures (`adaptive_reasoning`, `adaptive_code`, `adaptive_anti_deception`, `adaptive_memory`) additionally run an adapter LLM that rewrites the matched operation with task-specific identifiers; they require the Go or Super tier.

AutoGen reads `func.__name__` as the LLM-facing tool name. Python identifiers cannot contain hyphens, so the closure symbols here use underscores; the on-wire API mode strings stay hyphenated (`anti-deception`, `adaptive-anti-deception`). The translation lives inside each closure.

## Install

```bash
pip install autogen-ejentum
```

If AutoGen is not already installed:

```bash
pip install autogen-agentchat autogen-ext[openai] autogen-ejentum
```

## Configuration

```bash
export EJENTUM_API_KEY="ej_..."
```

Or pass `api_key=` to `ejentum_tools(...)`. Get a key at [ejentum.com/pricing](https://ejentum.com/pricing).

## Usage

```python
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_ejentum import ejentum_tools


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    agent = AssistantAgent(
        name="reviewer",
        model_client=model_client,
        tools=ejentum_tools(),
        system_message=(
            "Senior engineer. When a prompt pressures you to validate a decision "
            "before evidence, call anti_deception (or adaptive_anti_deception for "
            "high-stakes cases) with a 1-2 sentence framing of the integrity "
            "dynamic, then write."
        ),
    )

    await Console(agent.run_stream(
        task=(
            "We have spent three months on the GraphQL gateway. It's mostly "
            "done. Should we keep going or pivot to REST?"
        ),
    ))


asyncio.run(main())
```

AutoGen inspects each closure's `__name__` and Google-style docstring to generate the JSON schema the LLM sees.

### Wrap as `FunctionTool` (optional)

```python
from autogen_core.tools import FunctionTool
from autogen_ejentum import ejentum_tools

tools = [FunctionTool(fn, description=fn.__doc__) for fn in ejentum_tools()]
```

### Explicit API key

```python
tools = ejentum_tools(api_key="ej_...")
```

## Tool inventory

### Dynamic (all tiers)

| Closure | Mode string (on wire) | Library size |
|---|---|---:|
| `reasoning` | `reasoning` | 311 |
| `code` | `code` | 128 |
| `anti_deception` | `anti-deception` | 139 |
| `memory` | `memory` | 101 |

### Adaptive (Go or Super tier)

| Closure | Mode string (on wire) |
|---|---|
| `adaptive_reasoning` | `adaptive-reasoning` |
| `adaptive_code` | `adaptive-code` |
| `adaptive_anti_deception` | `adaptive-anti-deception` |
| `adaptive_memory` | `adaptive-memory` |

Each closure takes a single `query: str` argument and returns the injection as a string. Errors return as strings; closures do not raise.

## API reference

```python
from autogen_ejentum import ejentum_tools

ejentum_tools(
    api_key: str | None = None,
    api_url: str = "https://api.ejentum.com/harness/",
    timeout_seconds: float = 10.0,
) -> list[Callable[[str], Awaitable[str]]]
```

The eight returned callables are async functions with `__name__` set to `reasoning`, `code`, `anti_deception`, `memory`, `adaptive_reasoning`, `adaptive_code`, `adaptive_anti_deception`, `adaptive_memory`.

## Wire contract

```
POST https://api.ejentum.com/harness/
Headers: Authorization: Bearer <key>, Content-Type: application/json
Body:    { "query": <string>, "mode": <one of 8 mode strings> }
Response (200): [ { "<mode>": "<injection string>" } ]
Response (401|403|429): { "error": "..." }
```

Full wire contract, field structure of an injection, DAG syntax, and a canonical dynamic-vs-adaptive comparison on the same query are documented in the [ejentum-mcp README](https://github.com/ejentum/ejentum-mcp#wire-contract).

## ejentum-mcp alternative

The same eight tools are hosted as an MCP server at `https://api.ejentum.com/mcp`. AutoGen has MCP server support that consumes the endpoint with Bearer auth.

## Compatibility

- Python 3.10+
- `autogen-core>=0.4.0`
- `httpx>=0.27.0`

Works with AutoGen v0.4+ (the Microsoft + Berkeley async refactor). The legacy `pyautogen` (v0.2.x) uses `register_for_llm` / `register_for_execution` decorators rather than `AssistantAgent(tools=[...])`; this package does not target the legacy SDK.

## License

[MIT](./LICENSE)


## Measured effects

The Ejentum harness is benchmarked publicly under CC BY 4.0 at [github.com/ejentum/benchmarks](https://github.com/ejentum/benchmarks):

- **ELEPHANT** sycophancy: 5.8% composite on GPT-4o (40 real Reddit scenarios)
- **LiveCodeBench Hard**: 85.7% to 100% on Claude Opus (28 competitive programming tasks)
- **Memory retention**: 50% fewer stale facts served (20-turn implicit state changes)
- Plus per-harness numbers across BBH/CausalBench/MuSR, ARC-AGI-3, SciCode, and perception tasks

Methodology, scenarios, run scripts, and raw outputs are all in-repo.
