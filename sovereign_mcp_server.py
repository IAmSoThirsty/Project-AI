# (Substrate Interface Gateway)             [2026-04-09 04:26]
#                                          Status: Active
# PURPOSE: Project-AI MCP Server — exposes sovereign services to AI clients



"""
Project-AI Sovereign MCP Server

Exposes the Project-AI microservice mesh to any MCP-compatible AI client
(Claude Desktop, Cursor, etc.) via the Model Context Protocol.

Services exposed:
  - Legion API             (port 8002) — Sovereign AI Ambassador
  - Triumvirate            (port 8001) — Constitutional Governance Council
  - Sovereign Data Vault   (port 8000) — Zero-knowledge encryption layer

Transport: stdio — works out of the box with Cursor and Claude Desktop.

Install:
  pip install mcp httpx

Add to Cursor / Claude Desktop config (see bottom of this file).
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# ── Service base URLs ─────────────────────────────────────────────────────────

LEGION_BASE = "http://localhost:8002"
TRIUMVIRATE_BASE = "http://localhost:8001"
VAULT_BASE = "http://localhost:8000/api/v1"
TIMEOUT = 15.0

# ── Server ────────────────────────────────────────────────────────────────────

mcp = FastMCP("project_ai_mcp")


# ── Shared helpers ────────────────────────────────────────────────────────────


async def _get(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            return data
        return {"response": data}


async def _post(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            return data
        return {"response": data}


def _err(service: str, e: Exception) -> str:
    if isinstance(e, httpx.ConnectError):
        return f"Error: {service} is unreachable. Verify the service is running."
    if isinstance(e, httpx.HTTPStatusError):
        return f"Error: {service} returned HTTP {e.response.status_code}. {e.response.text}"
    if isinstance(e, httpx.TimeoutException):
        return f"Error: {service} timed out after {TIMEOUT}s."
    if isinstance(e, (ValueError, KeyError, TypeError)):
        return f"Error: {service} data breach/schema-mismatch - {type(e).__name__}: {e}"
    return f"Error: {service} — {type(e).__name__}: {e}"




#  LEGION — Port 8002                                                          #



class LegionChatInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(
        ...,
        description="Message to send to Legion through the governed /chat gateway.",
        min_length=1,
        max_length=8192,
    )
    context: str | None = Field(
        default=None,
        description="Optional context string to include with the message.",
    )


@mcp.tool(
    name="legion_chat",
    annotations={
        "title": "Send Message to Legion",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def legion_chat(params: LegionChatInput) -> str:
    """
    Send a message to Legion via the governed /chat gateway.

    All messages pass through the Triumvirate constitutional layer before
    Legion responds. This is the primary sovereign interaction endpoint.

    Args:
        params.message (str): The message to send.
        params.context (Optional[str]): Optional context.

    Returns:
        str: JSON response from Legion including the governed reply.
    """
    payload: dict = {"message": params.message}
    if params.context:
        payload["context"] = params.context
    try:
        result = await _post(f"{LEGION_BASE}/chat", payload)
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Legion /chat", e)
    except Exception as e:
        return _err("Legion /chat", e)


@mcp.tool(
    name="legion_status",
    annotations={
        "title": "Get Legion Agent Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def legion_status() -> str:
    """
    Retrieve Legion's detailed agent and EEG state from /status.

    Returns:
        str: JSON status object including agent state, EEG metrics, and mode.
    """
    try:
        result = await _get(f"{LEGION_BASE}/status")
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Legion /status", e)
    except Exception as e:
        return _err("Legion /status", e)


@mcp.tool(
    name="legion_learning_stats",
    annotations={
        "title": "Legion Real-Time Learning Stats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def legion_learning_stats() -> str:
    """
    Retrieve real-time learning metrics from Legion /learning/stats.

    Returns:
        str: JSON object containing current learning statistics.
    """
    try:
        result = await _get(f"{LEGION_BASE}/learning/stats")
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Legion /learning/stats", e)
    except Exception as e:
        return _err("Legion /learning/stats", e)




#  TRIUMVIRATE — Port 8001                                                     #



class IntentInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    intent: str = Field(
        ...,
        description=(
            "The intent or action to evaluate against the Triumvirate "
            "(Galahad / Cerberus / CodexDeus). Describe what you want to do."
        ),
        min_length=1,
        max_length=4096,
    )
    context: dict | None = Field(
        default=None,
        description="Optional structured context for the governance evaluation.",
    )


@mcp.tool(
    name="triumvirate_evaluate_intent",
    annotations={
        "title": "Evaluate Intent via Triumvirate",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def triumvirate_evaluate_intent(params: IntentInput) -> str:
    """
    Submit an intent for unified constitutional evaluation by the Triumvirate.

    Evaluated through three pillars:
      - Galahad   (ethics)
      - Cerberus  (security)
      - CodexDeus (constitutional law)

    Args:
        params.intent (str): The action or intent to evaluate.
        params.context (Optional[dict]): Structured context.

    Returns:
        str: JSON verdict including per-pillar rulings.
    """
    payload: dict = {"intent": params.intent}
    if params.context:
        payload["context"] = params.context
    try:
        result = await _post(f"{TRIUMVIRATE_BASE}/intent", payload)
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Triumvirate /intent", e)
    except Exception as e:
        return _err("Triumvirate /intent", e)


@mcp.tool(
    name="triumvirate_audit",
    annotations={
        "title": "Retrieve Constitutional Audit Log",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def triumvirate_audit() -> str:
    """
    Retrieve records from the DurableLedger via Triumvirate /audit.

    Returns:
        str: JSON audit records from the constitutional ledger.
    """
    try:
        result = await _get(f"{TRIUMVIRATE_BASE}/audit")
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Triumvirate /audit", e)
    except Exception as e:
        return _err("Triumvirate /audit", e)


@mcp.tool(
    name="triumvirate_tarl_rules",
    annotations={
        "title": "Get Current TARL Rule Set",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def triumvirate_tarl_rules() -> str:
    """
    Retrieve the current Advanced Regulator Layer (TARL) rule set from /tarl.

    Returns:
        str: JSON object containing the active constitutional rules.
    """
    try:
        result = await _get(f"{TRIUMVIRATE_BASE}/tarl")
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Triumvirate /tarl", e)
    except Exception as e:
        return _err("Triumvirate /tarl", e)


@mcp.tool(
    name="triumvirate_health",
    annotations={
        "title": "Triumvirate Health Check",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def triumvirate_health() -> str:
    """
    Check Triumvirate + PSIA service health.

    Returns:
        str: JSON health object.
    """
    try:
        result = await _get(f"{TRIUMVIRATE_BASE}/health")
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Triumvirate /health", e)
    except Exception as e:
        return _err("Triumvirate /health", e)




#  SOVEREIGN DATA VAULT — Port 8000                                            #



class VaultEncryptInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    data: str = Field(
        ...,
        description="Plaintext data to encrypt using zero-knowledge keys.",
        min_length=1,
    )
    capability: str | None = Field(
        default=None,
        description="Optional capability token to bind to this encryption.",
    )


class VaultDecryptInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    ciphertext: str = Field(
        ...,
        description="Encrypted ciphertext to decrypt.",
        min_length=1,
    )
    capability_token: str = Field(
        ...,
        description="Valid capability token required for decryption.",
        min_length=1,
    )


@mcp.tool(
    name="vault_encrypt",
    annotations={
        "title": "Encrypt Data via Sovereign Vault",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def vault_encrypt(params: VaultEncryptInput) -> str:
    """
    Encrypt data using the Sovereign Data Vault zero-knowledge layer.

    Args:
        params.data (str): Plaintext to encrypt.
        params.capability (Optional[str]): Capability token to bind.

    Returns:
        str: JSON response containing ciphertext and vault metadata.
    """
    payload: dict = {"data": params.data}
    if params.capability:
        payload["capability"] = params.capability
    try:
        result = await _post(f"{VAULT_BASE}/vault/encrypt", payload)
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Vault /encrypt", e)
    except Exception as e:
        return _err("Vault /encrypt", e)


@mcp.tool(
    name="vault_decrypt",
    annotations={
        "title": "Decrypt Data via Sovereign Vault",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def vault_decrypt(params: VaultDecryptInput) -> str:
    """
    Decrypt data using a valid capability token via the Sovereign Data Vault.

    Args:
        params.ciphertext (str): The encrypted ciphertext.
        params.capability_token (str): Valid capability token.

    Returns:
        str: JSON response containing the decrypted plaintext.
    """
    payload = {
        "ciphertext": params.ciphertext,
        "capability_token": params.capability_token,
    }
    try:
        result = await _post(f"{VAULT_BASE}/vault/decrypt", payload)
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Vault /decrypt", e)
    except Exception as e:
        return _err("Vault /decrypt", e)


@mcp.tool(
    name="vault_health",
    annotations={
        "title": "Sovereign Data Vault Health Check",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def vault_health() -> str:
    """
    Check Sovereign Data Vault liveness and readiness.

    Returns:
        str: JSON health object.
    """
    try:
        result = await _get(f"{VAULT_BASE}/health")
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return _err("Vault /health", e)
    except Exception as e:
        return _err("Vault /health", e)




#  AGGREGATE — Full Mesh Health                                                #



@mcp.tool(
    name="sovereign_mesh_health",
    annotations={
        "title": "Full Sovereign Mesh Health",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sovereign_mesh_health() -> str:
    """
    Poll all sovereign services and return an aggregate health report.

    Checks Legion (8002), Triumvirate (8001), and Vault (8000) in parallel.

    Returns:
        str: JSON report with per-service status and overall mesh state
             (SOVEREIGN if all UP, DEGRADED otherwise).
    """
    async def check(name: str, url: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url)
                return {"service": name, "status": "UP", "http": r.status_code}
        except httpx.ConnectError:
            return {"service": name, "status": "UNREACHABLE"}
        except httpx.HTTPStatusError as ex:
            return {"service": name, "status": "ERROR", "http": ex.response.status_code}
        except Exception as ex:
            return {"service": name, "status": "ERROR", "detail": str(ex)}

    results = await asyncio.gather(
        check("legion",      f"{LEGION_BASE}/health"),
        check("triumvirate", f"{TRIUMVIRATE_BASE}/health"),
        check("vault",       f"{VAULT_BASE}/health"),
    )

    all_up = all(r["status"] == "UP" for r in results)
    return json.dumps(
        {
            "mesh_status": "SOVEREIGN" if all_up else "DEGRADED",
            "services": list(results),
        },
        indent=2,
    )




#  Entry Point                                                                 #



if __name__ == "__main__":
    mcp.run()




#  CONFIGURATION                                                               #


#
# CURSOR (settings.json):
# ─────────────────────────────────────────────────────────────────────────────
# "mcpServers": {
#   "project-ai": {
#     "command": "python",
#     "args": ["C:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/sovereign_mcp_server.py"]
#   }
# }
#
# CLAUDE DESKTOP (claude_desktop_config.json):
# ─────────────────────────────────────────────────────────────────────────────
# {
#   "mcpServers": {
#     "project-ai": {
#       "command": "python",
#       "args": ["C:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/sovereign_mcp_server.py"]
#     }
#   }
# }
#
# TOOLS EXPOSED (13 total):
# ─────────────────────────────────────────────────────────────────────────────
#   legion_chat                    — governed interaction gateway
#   legion_status                  — agent + EEG state
#   legion_learning_stats          — real-time learning metrics
#   triumvirate_evaluate_intent    — constitutional verdict (all 3 pillars)
#   triumvirate_audit              — DurableLedger records
#   triumvirate_tarl_rules         — active TARL rule set
#   triumvirate_health             — PSIA + Triumvirate health
#   vault_encrypt                  — zero-knowledge encryption
#   vault_decrypt                  — capability-based decryption
#   vault_health                   — vault liveness
#   sovereign_mesh_health          — aggregate mesh status
