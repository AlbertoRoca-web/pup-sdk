# app.py at repo root

import os
import logging

from pup_sdk.web.app import create_app
from pup_sdk.client import PupClient

# simple logger so we can see what PupClient.from_env() does at startup
logger = logging.getLogger("pup-debug")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- main FastAPI app that uvicorn will serve ---
# IMPORTANT: do NOT pass a "client=" kwarg; create_app() doesn't support it.
app = create_app()


def get_client_from_env() -> PupClient:
    """
    Helper for /debug/env: build a throwaway PupClient from env
    so we can see how it would be configured.
    This does NOT change whatever client the SDK’s web app is using internally.
    """
    client = PupClient.from_env()
    logger.warning(
        "PUPCLIENT ENV CHECK demo_mode=%s open_api_key=%s syn_api_key=%s base_url=%s",
        getattr(client, "demo_mode", None),
        "set" if getattr(client, "open_api_key", None) else "missing",
        "set" if getattr(client, "syn_api_key", None) else "missing",
        getattr(client, "base_url", None),
    )
    return client


@app.get("/debug/env")
async def debug_env():
    """
    Debug endpoint to confirm:
      - HF env vars are present
      - What PupClient.from_env() would see
    """
    client = get_client_from_env()

    return {
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),
        "client_demo_mode": getattr(client, "demo_mode", None),
        "client_has_open_key": bool(getattr(client, "open_api_key", None)),
        "client_has_syn_key": bool(getattr(client, "syn_api_key", None)),
        "client_base_url": getattr(client, "base_url", None),
    }
