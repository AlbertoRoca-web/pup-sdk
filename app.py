import os
import logging

from pup_sdk.web.app import create_app
from pup_sdk.client import PupClient

logger = logging.getLogger("pup-debug")

# Build a single shared client from environment - this will:
# - Respect ALBERTO_API_URL / PUP_BACKEND_URL when set
# - Pick SYN_API_KEY or OPEN_API_KEY
# - Set demo_mode=True if no keys are present
_client = PupClient.from_env()

logger.warning(
    "PUPCLIENT ENV CHECK demo_mode=%s api_key=%s base_url=%s",
    _client.demo_mode,
    "set" if bool(getattr(_client, "api_key", None)) else "missing",
    getattr(_client, "base_url", None),
)

# Pass the client into the web app so both the UI and /debug/env
# are using the exact same PupClient instance.
app = create_app(client=_client)


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to inspect environment + client configuration."""
    client = getattr(app.state, "client", None)

    return {
        # Raw environment flags
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),
        "has_ALBERTO_API_URL": bool(os.getenv("ALBERTO_API_URL")),
        "ALBERTO_API_URL": os.getenv("ALBERTO_API_URL"),
        "has_PUP_BACKEND_URL": bool(os.getenv("PUP_BACKEND_URL")),
        "PUP_BACKEND_URL": os.getenv("PUP_BACKEND_URL"),

        # Client-derived view
        "client_demo_mode": bool(getattr(client, "demo_mode", True)) if client else True,
        "client_has_api_key": bool(getattr(client, "api_key", None)) if client else False,
        "client_base_url": getattr(client, "base_url", None) if client else None,
    }
