# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / agent_orchestrator.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / agent_orchestrator.py

#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #


# AGENT ORCHESTRATOR
# Seamless Microservice & LLM Integration

import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"
DEFAULT_SERVICE_URL = "http://localhost:8000"

def agent_call(agent_model, prompt, service_endpoint=None, **kwargs):
    """
    Orchestrates a call between an LLM agent and a microservice.
    """
    if service_endpoint:
        # Call microservice first
        url = f"{DEFAULT_SERVICE_URL}/{service_endpoint}"
        try:
            resp = requests.post(url, json={"data": prompt, **kwargs})
            resp.raise_for_status()
            service_output = resp.json().get("result", "")
            prompt = f"{prompt}\nService result: {service_output}"
        except Exception as e:
            print(f"Service call failed: {e}")
            prompt = f"{prompt}\nService call ERROR: {e}"
    
    payload = {
        "model": agent_model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        r = requests.post(OLLAMA_API, json=payload)
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        return f"Agent call failed: {e}"
