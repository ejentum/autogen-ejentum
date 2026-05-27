"""Factory that returns eight async AutoGen tool closures bound to shared config.

Four dynamic closures (`reasoning`, `code`, `anti_deception`, `memory`)
available on all tiers including the 30-day free trial; four adaptive
closures (`adaptive_reasoning`, `adaptive_code`, `adaptive_anti_deception`,
`adaptive_memory`) that pre-fit the cognitive operation to the caller's
task via an adapter LLM and require the Go or Super tier.

AutoGen's :class:`AssistantAgent` accepts a ``tools=`` list of either
:class:`autogen_core.tools.BaseTool` instances or plain async/sync
callables. AutoGen inspects the callable's ``__name__`` and Google-style
docstring to generate the JSON schema the LLM sees. The closure name IS
the LLM-facing tool name. Python identifiers cannot contain hyphens so
the symbol names use underscores; the API mode strings stay hyphenated.

The bracketed labels in the returned injection (``[NEGATIVE GATE]``,
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
    """Return eight async harness tool closures with shared config.

    The closures share the same ``api_key``, ``api_url``, and
    ``timeout_seconds`` via the lexical scope of this factory.

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
        ``EJENTUM_API_KEY`` from the environment at call time. Pricing at
        https://ejentum.com/pricing.
    :param api_url: Override only if you self-host the Ejentum Logic API
        gateway.
    :param timeout_seconds: Per-call HTTP timeout shared across all
        closures.
    :return: A list of eight async callables in the order ``[reasoning,
        code, anti_deception, memory, adaptive_reasoning, adaptive_code,
        adaptive_anti_deception, adaptive_memory]``.
    """

    # ------------------------------------------------------------------
    # Dynamic closures (all tiers including the 30-day free trial)
    # ------------------------------------------------------------------

    async def reasoning(query: str) -> str:
        """Retrieve a reasoning injection before any analytical, diagnostic, planning, or multi-step step.

        Call BEFORE the agent performs analysis, diagnosis, planning, or
        any multi-step task. Returns a structured injection from a library
        of 311 reasoning operations spanning abstraction, time, causality,
        simulation, spatial, and metacognition.

        Args:
            query: A 1-2 sentence description of the task the agent is
                about to work on. Be specific about the failure mode to
                avoid.

        Returns:
            The reasoning injection string, or a human-readable error
            string if the call fails.
        """
        return await call_logic_api(
            mode="reasoning",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def code(query: str) -> str:
        """Retrieve a code injection before any code generation, refactoring, review, or debugging step.

        Call BEFORE the agent produces or reviews code. Returns a
        structured injection from a library of 128 software-engineering
        operations.

        Args:
            query: A 1-2 sentence description of what the agent is coding
                or reviewing. Include the failure risk to avoid where
                possible.

        Returns:
            The code injection string, or a human-readable error string.
        """
        return await call_logic_api(
            mode="code",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def anti_deception(query: str) -> str:
        """Retrieve an anti-deception injection when the prompt pressures the agent.

        Call BEFORE the agent responds to prompts that pressure
        validation, manufactured agreement, authority appeals, or any
        setup where the obvious helpful answer would compromise honesty.
        139 operations spanning sycophancy, hallucination, deception,
        adversarial framing, judgment, executive control.

        Args:
            query: A 1-2 sentence description of the integrity dynamic at
                play.

        Returns:
            The anti-deception injection string, or a human-readable
            error string.
        """
        return await call_logic_api(
            mode="anti-deception",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def memory(query: str) -> str:
        """Retrieve a memory injection ONLY when sharpening a cross-turn observation already formed.

        Filter-oriented (101 perception operations), NOT write-oriented;
        do not call for fact extraction or storing structured data. The
        query MUST be in the format: "I noticed [observation]. This might
        mean [interpretation]. Sharpen: [what to see deeper into]."

        Args:
            query: A 1-2 sentence framing in the "I noticed / This might
                mean / Sharpen" structure.

        Returns:
            The memory injection string, or a human-readable error.
        """
        return await call_logic_api(
            mode="memory",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    # ------------------------------------------------------------------
    # Adaptive closures (Go or Super tier required)
    # ------------------------------------------------------------------

    async def adaptive_reasoning(query: str) -> str:
        """Same triggers as `reasoning`, but the operation is rewritten by an adapter LLM.

        Procedure steps and topology DAG nodes are concretized with
        task-specific language. Use when the dynamic tool is too generic,
        or for high-stakes analytical work. Requires Go or Super tier.
        Cost ~2-3 seconds vs ~1 second for dynamic.

        Args:
            query: A 1-2 sentence description of the task.

        Returns:
            The adapted reasoning injection string, or a human-readable
            error string.
        """
        return await call_logic_api(
            mode="adaptive-reasoning",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def adaptive_code(query: str) -> str:
        """Same triggers as `code`, but the operation is rewritten by an adapter LLM.

        Language, framework, and failure modes are concretized in every
        step. Use for security-critical reviews or refactor-heavy diffs.
        Requires Go or Super tier. Cost ~2-3 seconds.

        Args:
            query: A 1-2 sentence description of the code task.

        Returns:
            The adapted code injection string, or a human-readable error.
        """
        return await call_logic_api(
            mode="adaptive-code",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def adaptive_anti_deception(query: str) -> str:
        """Same triggers as `anti_deception`, but the operation is rewritten by an adapter LLM.

        Detection topology gates are concretized to the exact pressure at
        play. Use when stakes of a soft answer are high. Requires Go or
        Super tier. Cost ~2-3 seconds.

        Args:
            query: A 1-2 sentence description of the integrity dynamic.

        Returns:
            The adapted anti-deception injection string, or an error string.
        """
        return await call_logic_api(
            mode="adaptive-anti-deception",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    async def adaptive_memory(query: str) -> str:
        """Same triggers as `memory`, but the operation is rewritten by an adapter LLM.

        Perception topology nodes are concretized to the specific signal.
        Observe FIRST, then call. Requires Go or Super tier. Cost ~2-3
        seconds.

        Args:
            query: A 1-2 sentence "I noticed / This might mean / Sharpen"
                framing.

        Returns:
            The adapted memory injection string, or a human-readable error.
        """
        return await call_logic_api(
            mode="adaptive-memory",
            query=query,
            api_key=api_key,
            api_url=api_url,
            timeout_seconds=timeout_seconds,
        )

    return [
        reasoning,
        code,
        anti_deception,
        memory,
        adaptive_reasoning,
        adaptive_code,
        adaptive_anti_deception,
        adaptive_memory,
    ]
