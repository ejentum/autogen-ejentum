# autogen-ejentum

[AutoGen](https://microsoft.github.io/autogen/) tools for the [Ejentum](https://ejentum.com) Reasoning Harness. `ejentum_tools()` returns four async tool closures (`harness_reasoning`, `harness_code`, `harness_anti_deception`, `harness_memory`) that AutoGen's `AssistantAgent` calls before generating.

Each operation in the Ejentum library (679 of them, organized across four harnesses) is engineered in **two layers**:

- a **natural-language procedure** the model can read, naming the steps to take and the failure pattern to refuse, and
- an **executable reasoning topology**: a graph-shaped plan over those steps. The plan names explicit decision points where the model branches, parallel branches that run and rejoin, bounded loops that run until convergence, named meta-cognitive moments where the model is asked to stop, look at its own working, and re-enter at a specific step, plus escape paths for when the prescribed plan stops fitting the task at hand.

The natural-language layer tells the model *what* to do. The topology layer pins down *how* those steps connect: where to decide, where to loop, where to stop and look at itself. Together they act as a persistent attention anchor that survives long context windows and multi-turn execution chains, which is precisely where a model's own reasoning template typically decays.

## Installation

```bash
pip install autogen-ejentum
```

If you don't already have AutoGen installed:

```bash
pip install autogen-agentchat autogen-ext[openai] autogen-ejentum
```

## Configuration

Get an Ejentum API key at <https://ejentum.com/pricing> (free and paid tiers) and set it in your environment:

```bash
export EJENTUM_API_KEY="zpka_..."
```

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
        tools=ejentum_tools(),  # reads EJENTUM_API_KEY from env
        system_message=(
            "You are a senior engineer. When a prompt pressures you to "
            "validate a decision before evidence, call "
            "harness_anti_deception with a 1-2 sentence framing of the "
            "integrity dynamic at play, then write."
        ),
    )

    await Console(agent.run_stream(
        task=(
            "We've spent three months on the GraphQL gateway. It's mostly "
            "done. Should we keep going or pivot to REST?"
        ),
    ))


asyncio.run(main())
```

The agent reads each closure's name + Google-style docstring and routes to the matching `harness_*` tool. AutoGen handles JSON schema generation; you don't write one.

### Explicit API key

```python
tools = ejentum_tools(api_key="zpka_...")
```

### Wrap as a BaseTool (if you prefer)

```python
from autogen_core.tools import FunctionTool
from autogen_ejentum import ejentum_tools

tools = [FunctionTool(fn, description=fn.__doc__) for fn in ejentum_tools()]
```

## The four tools

| Closure | Best for | Library size |
|---|---|---|
| `harness_reasoning` | Analytical, diagnostic, planning, multi-step tasks spanning abstraction, time, causality, simulation, spatial, and metacognition | 311 operations |
| `harness_code` | Code generation, refactoring, review, and debugging across the software-engineering layer | 128 operations |
| `harness_anti_deception` | Prompts that pressure the agent to validate, certify, or soften an honest assessment | 139 operations |
| `harness_memory` | Sharpening an observation already formed about cross-turn drift. Filter-oriented, not write-oriented. Format query as `"I noticed X. This might mean Y. Sharpen: Z."` | 101 operations |

## What an injection looks like

A real `reasoning` mode response on the query `investigate why our nightly ETL job has started failing intermittently over the past two weeks; nothing in the code or schema has changed`:

```
[NEGATIVE GATE]
The server's response time was accepted as average, despite a suspicious
rhythm break in its timing pattern.

[PROCEDURE]
Step 1: Establish baseline timing profiles by extracting historical
durations and intervals for each event type. Step 2: Compare each observed
timing against its baseline and compute deviation magnitude. Step 3:
Classify anomalies as too fast, too slow, too early, or too late, and rank
by severity. ... Step 5: If deviation exceeds two standard deviations,
probe root cause by tracing upstream dependencies. ...

[REASONING TOPOLOGY]
S1:durations -> FIXED_POINT[baselines] -> N{dismiss_timing_deviations_
without_investigation} -> for_each: S2:compare -> S3:deviation ->
G1{>2sigma?} --yes-> S4:classify -> S5:probe_cause -> FLAG -> continue --no->
S6:validate -> continue -> all_checked -> OUT:anomaly_report

[TARGET PATTERN]
Establish timing baselines by extracting historical response intervals.
Compare current server response time to this baseline. ...

[FALSIFICATION TEST]
If no event timing is flagged as suspiciously fast or slow relative to
baseline, temporal anomaly detection was not active.

Amplify: timing baseline comparison; anomaly classification; security
context elevation
Suppress: average timing acceptance; outlier normalization
```

The agent reads both the natural-language `[PROCEDURE]` and the graph-logic `[REASONING TOPOLOGY]` before generating its user-facing answer. The bracketed labels are instructions to the agent, not content to display.

## API reference

```python
from autogen_ejentum import ejentum_tools

ejentum_tools(
    api_key: str | None = None,
    api_url: str = "https://ejentum-main-ab125c3.zuplo.app/logicv1/",
    timeout_seconds: float = 10.0,
) -> list[Callable[[str], Awaitable[str]]]
```

The four returned callables are async functions with `__name__` set to `harness_reasoning`, `harness_code`, `harness_anti_deception`, `harness_memory`. Each accepts a single `query: str` argument. Errors are returned as human-readable strings (no exceptions cross the tool boundary, so an agent step never crashes the run).

> **MCP alternative.** This package wraps the Logic API REST gateway with async `httpx`. AutoGen also has MCP server support; the same four harness tools are hosted at `https://api.ejentum.com/mcp` with Bearer auth. The PyPI package skips MCP setup and keeps the dep weight tiny.

## Compatibility

- Python 3.10+
- `autogen-core>=0.4.0`
- `httpx>=0.27.0`

Works with AutoGen v0.4+ (the Microsoft + Berkeley async refactor). Not tested against the legacy `pyautogen` (v0.2.x); the older one uses `register_for_llm` / `register_for_execution` decorators rather than `AssistantAgent(tools=[...])`.

## Resources

- Ejentum homepage: <https://ejentum.com>
- Pricing: <https://ejentum.com/pricing>
- API reference: <https://ejentum.com/docs/api_reference>
- "Why LLM Agents Fail" essay: <https://ejentum.com/blog/why-llm-agents-fail>
- "Under Pressure" research paper: <https://doi.org/10.5281/zenodo.19392715>
- AutoGen documentation: <https://microsoft.github.io/autogen>

## License

[MIT](./LICENSE)
