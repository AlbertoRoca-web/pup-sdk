import os
import logging
from pup_sdk.web.app import create_app
from pup_sdk.client import PupClient

logger = logging.getLogger("pup-debug")

# build a single client instance and inject it into the web app
def build_client_from_env() -> PupClient:
    client = PupClient.from_env()
    logger.warning(
        "PUPCLIENT ENV CHECK demo_mode=%s api_key=%s base_url=%s",
        client.demo_mode,
        "set" if bool(getattr(client, "api_key", None)) else "missing",
        getattr(client, "base_url", None),
    )
    return client

pup_client = build_client_from_env()
app = create_app(client=pup_client)


@app.get("/debug/env")
async def debug_env():
    client = pup_client
    return {
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),
        "client_demo_mode": client.demo_mode,
        "client_has_api_key": bool(getattr(client, "api_key", None)),
        "client_base_url": getattr(client, "base_url", None),
    }
