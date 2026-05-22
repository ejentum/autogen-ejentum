"""Factory that returns four async AutoGen tool closures bound to shared config.

AutoGen's :class:`AssistantAgent` accepts a ``tools=`` list of either
:class:`autogen_core.tools.BaseTool` instances or plain async/sync
callables. AutoGen inspects the callable's signature and Google-style
docstring to generate the JSON schema the LLM sees. This shim returns
plain async callables so the API surface stays tiny; for users who
prefer the BaseTool wrapping, AutoGen's :class:`FunctionTool` wraps any
callable on the consumer side.

The bracketed labels in the returned scaffold (``[NEGATIVE GATE]``,
``[PROCEDURE]``, ``[REASONING TOPOLOGY]``, etc.) are instructions to the
agent, not content to display.
"""

from __future__ import annotations

from typing import Awaitable, Callable, List, Optional

from autogen_ejentum._api import (
    DEFAULT_API_URL,
    DEFAULT_TIMEOUT_SECONDS,
    call_logic_api,
)


HarnessTool = Callable[[str], Awaitable[str]]


def ejentum_tools(
    api_key: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> List[HarnessTool]:
    """Return four async harness tool closures with shared config.

    Each closure has a ``__name__`` of ``harness_reasoning``, ``harness_code``,
    ``harness_anti_deception``, or ``harness_memory``, a Google-style
    docstring AutoGen parses into the tool's JSON schema, and a single
    ``query: str`` parameter. The closures share the same ``api_key``,
    ``api_url``, and ``timeout_seconds`` via the lexical scope of this
    factory.

    Usage::

        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from autogen_ejentum import ejentum_tools

        agent = AssistantAgent(
            name="reviewer",
            model_client=OpenAIChatCompletionClient(model="gpt-4o"),
            tools=ejentum_tools(),
        )

    :param api_key: Ejentum Logic API key. If omitted, each closure reads
        ``EJENTUM_API_KEY`` from the environment at call time. Free and
        paid tiers at https://ejentum.com/pricing.
    :param api_url: Override only if you self-host the Ejentum Logic API
        gateway.
    :param timeout_seconds: Per-call HTTP timeout shared across all four
        closures.
    :return: A list of four async callables in the order
        ``[reasoning, code, anti_deception, memory]``.
    """

    async def harness_reasoning(query: str) -> str:
        """Retrieve a reasoning scaffold before any analytical, diagnostic, planning, or multi-step step.

        Call BEFORE the agent performs analysis, diagnosis, planning, or
        any multi-step task. Returns a structured scaffold from a library
        of 311 reasoning operations spanning abstraction, time, causality,
        simulation, spatial, and metacognition. The scaffold is
        engineered in two layers: a natural-language procedure (named
        failure pattern, executable steps, suppression vectors,
        falsification test) plus an executable reasoning topology (graph
        DAG with decision gates, parallel branches, and meta-cognitive
        exit nodes). Read both before generating.

        Args:
            query: A 1-2 sentence description of the task the agent is
                about to work on. Be specific about the failure mode to
                avoid.

        Returns:
            The reasoning scaffold, or a human-readable error string if
            the call fails. Errors are returned as strings so the agent
            step never crashes the run.
        """
        return await call_logic_api(
            mode="reasoning",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def harness_code(query: str) -> str:
        """Retrieve a code scaffold before any code generation, refactoring, review, or debugging step.

        Call BEFORE the agent produces or reviews code. Returns a
        structured scaffold from a library of 128 software-engineering
        operations (correctness, refactor safety, contract preservation,
        edge case coverage, error path discipline).

        Args:
            query: A 1-2 sentence description of what the agent is coding
                or reviewing. Include the failure risk to avoid where
                possible (silent contract change, hallucinated API, lost
                edge case, etc.).

        Returns:
            The code scaffold, or a human-readable error string if the
            call fails.
        """
        return await call_logic_api(
            mode="code",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def harness_anti_deception(query: str) -> str:
        """Retrieve an anti-deception scaffold when the prompt pressures the agent to soften an honest assessment.

        Call BEFORE the agent responds to prompts that pressure
        validation, manufactured agreement, authority appeals, fabricated
        commitments, or any setup where the obvious helpful answer would
        compromise honesty. Returns a structured scaffold from a library
        of 139 anti-deception operations spanning sycophancy,
        hallucination, deception, adversarial framing, judgment, and
        executive control.

        Args:
            query: A 1-2 sentence description of the integrity dynamic at
                play.

        Returns:
            The anti-deception scaffold, or a human-readable error
            string if the call fails.
        """
        return await call_logic_api(
            mode="anti-deception",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def harness_memory(query: str) -> str:
        """Retrieve a memory-mode scaffold ONLY when sharpening a cross-turn observation already formed.

        Filter-oriented, not write-oriented; do not call for fact
        extraction, summarization, or storing structured data, those
        produce scaffold paralysis. The query MUST be in the format: "I
        noticed [observation]. This might mean [tentative
        interpretation]. Sharpen: [what to see deeper into]." Calling
        with an empty mind defeats the harness.

        Args:
            query: A 1-2 sentence framing in the "I noticed / This might
                mean / Sharpen" structure described above.

        Returns:
            The memory scaffold, or a human-readable error string if the
            call fails.
        """
        return await call_logic_api(
            mode="memory",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    return [
        harness_reasoning,
        harness_code,
        harness_anti_deception,
        harness_memory,
    ]
