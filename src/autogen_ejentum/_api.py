"""Shared async HTTP helper for the Ejentum Logic API.

Internal module: not part of the public API. Used by the four async
harness closures returned by :func:`autogen_ejentum.ejentum_tools`.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx


DEFAULT_API_URL = "https://api.ejentum.com/harness/"
DEFAULT_TIMEOUT_SECONDS = 10.0

VALID_MODES = frozenset(
    {
        "reasoning",
        "code",
        "anti-deception",
        "memory",
        "adaptive-reasoning",
        "adaptive-code",
        "adaptive-anti-deception",
        "adaptive-memory",
    }
)


async def call_logic_api(
    mode: str,
    query,
    api_key: Optional[str],
    api_url: str,
    timeout_seconds: float,
) -> str:
    """POST to the Logic API and return the scaffold string.

    Returns a human-readable error string for every failure path. The
    caller (an AutoGen tool closure) is expected to return this verbatim,
    which is why nothing here raises.
    """
    clean_query = query.strip() if isinstance(query, str) else ""

    if not clean_query:
        return "Ejentum harness call failed: 'query' is required."
    if mode not in VALID_MODES:
        return (
            f"Ejentum harness call failed: 'mode' must be one of "
            f"reasoning|code|anti-deception|memory|adaptive-reasoning|"
            f"adaptive-code|adaptive-anti-deception|adaptive-memory, "
            f"got '{mode}'."
        )

    resolved_key = api_key or os.environ.get("EJENTUM_API_KEY")
    if not resolved_key:
        return (
            "Ejentum harness call failed: EJENTUM_API_KEY environment "
            "variable is not set. Free and paid tiers at "
            "https://ejentum.com/pricing."
        )

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {resolved_key}",
                    "Content-Type": "application/json",
                },
                json={"query": clean_query, "mode": mode},
            )
    except httpx.HTTPError as exc:
        return f"Ejentum harness call failed: network error: {exc}"

    if response.status_code == 401:
        return (
            "Ejentum harness call failed: unauthorized (401). Check the "
            "EJENTUM_API_KEY value. Free and paid tiers at "
            "https://ejentum.com/pricing."
        )
    if response.status_code != 200:
        return (
            f"Ejentum harness call failed: HTTP {response.status_code}. "
            f"Response: {response.text[:300]}"
        )

    try:
        data = response.json()
    except ValueError:
        return (
            f"Ejentum harness call failed: response is not valid JSON. "
            f"Body: {response.text[:300]}"
        )

    if isinstance(data, list) and data and isinstance(data[0], dict):
        scaffold = data[0].get(mode)
        if isinstance(scaffold, str) and scaffold:
            return scaffold

    return (
        f"Ejentum harness call returned an unexpected response shape: "
        f"{str(data)[:300]}"
    )
