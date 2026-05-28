"""autogen-ejentum: AutoGen tools for the Ejentum Reasoning Harness.

Exposes :func:`ejentum_tools`, a factory that returns eight async tool
closures bound to a shared ``api_key`` / ``api_url`` / ``timeout_seconds``
config. Four are dynamic (``reasoning``, ``code``, ``anti_deception``,
``memory``); four are adaptive (``adaptive_reasoning``, ``adaptive_code``,
``adaptive_anti_deception``, ``adaptive_memory``) that pre-fit the cognitive
operation to the caller's task via an adapter LLM. Adaptive closures require
the Go or Super tier.

Pass the list to :class:`autogen_agentchat.agents.AssistantAgent` via its
``tools=`` parameter; AutoGen inspects each closure's ``__name__`` and
Google-style docstring to generate the JSON schema the LLM sees. Closure
symbols use underscores because Python identifiers cannot contain hyphens;
the on-wire API mode strings stay hyphenated.

Each call retrieves a task-matched cognitive operation from a library of 679,
engineered in two layers: a natural-language procedure plus an executable
reasoning topology (graph DAG with gates, parallel branches, and
meta-cognitive exit nodes).

Pricing at https://ejentum.com/pricing.
"""

from autogen_ejentum.tools import HarnessTool, ejentum_tools
from autogen_ejentum._api import (
    DEFAULT_API_URL,
    DEFAULT_TIMEOUT_SECONDS,
    VALID_MODES,
    call_logic_api,
)

__all__ = [
    "ejentum_tools",
    "HarnessTool",
    "call_logic_api",
    "DEFAULT_API_URL",
    "DEFAULT_TIMEOUT_SECONDS",
    "VALID_MODES",
]
__version__ = "0.2.0"
