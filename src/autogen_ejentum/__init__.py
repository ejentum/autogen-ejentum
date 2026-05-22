"""autogen-ejentum: AutoGen tools for the Ejentum Reasoning Harness.

Exposes :func:`ejentum_tools`, a factory that returns four async tool
closures (one per harness) bound to a shared ``api_key`` /
``api_url`` / ``timeout_seconds`` config. Pass the list to
:class:`autogen_agentchat.agents.AssistantAgent` via its ``tools=``
parameter; AutoGen inspects each closure's signature and Google-style
docstring to generate the JSON schema the LLM sees.

Each call retrieves a task-matched cognitive operation from a library
of 679, engineered in two layers: a natural-language procedure plus an
executable reasoning topology (graph DAG with gates, parallel branches,
and meta-cognitive exit nodes).

Free and paid tiers at https://ejentum.com/pricing.
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
__version__ = "0.1.0"
