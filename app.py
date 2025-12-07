# app.py at repo root

import os
import logging

from pup_sdk.web.app import create_app
from pup_sdk.client import PupClient

logger = logging.getLogger("pup-debug")

# --------------------------------------------------------------------
# 1) Build a single PupClient from the actual env, then override
#    demo_mode if we clearly have keys.
# --------------------------------------------------------------------
def build_client_from_env() -> PupClient:
    client = PupClient.from_env()

    has_open = bool(os.getenv("OPEN_API_KEY"))
    has_syn = bool(os.getenv("SYN_API_KEY"))

    # Log what PupClient *thinks* it has
    logger.warning(
        "PUPCLIENT ENV CHECK demo_mode=%s open_key=%s syn_key=%s",
        getattr(client, "demo_mode", None),
        bool(getattr(client, "open_api_key", None)),
        bool(getattr(client, "syn_api_key", None)),
    )

    # If keys exist in the env but client is still in demo mode,
    # forcibly turn demo_mode off.
    if (has_open or has_syn) and getattr(client, "demo_mode", None):
        logger.warning(
            "PUPCLIENT: keys present but demo_mode=True -> overriding to False"
        )
        try:
            client.demo_mode = False
        except Exception as e:
            logger.error("Failed to override demo_mode on client: %r", e)

    return client


# Single global client that the web app will use
pup_client = build_client_from_env()

# --------------------------------------------------------------------
# 2) Create the FastAPI app using that client.
#    If your version of create_app does NOT accept 'client=',
#    remove `client=pup_client` below and just call create_app(),
#    but keep the rest of this file the same.
# --------------------------------------------------------------------
try:
    app = create_app(client=pup_client)
except TypeError:
    # Fallback for older create_app signatures: no 'client' arg
    logger.warning(
        "create_app() does not accept a 'client' parameter; "
        "using default create_app() but keeping pup_client for debug."
    )
    app = create_app()


# --------------------------------------------------------------------
# 3) Debug endpoint: show both raw env and PupClient’s view
# --------------------------------------------------------------------
@app.get("/debug/env")
async def debug_env():
    return {
        # Raw env view
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),

        # What PupClient actually sees
        "client_demo_mode": getattr(pup_client, "demo_mode", None),
        "client_has_open_key": bool(getattr(pup_client, "open_api_key", None)),
        "client_has_syn_key": bool(getattr(pup_client, "syn_api_key", None)),
    }
