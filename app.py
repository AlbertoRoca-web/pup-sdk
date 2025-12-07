import os
import logging

from pup_sdk.web.app import create_app
from pup_sdk.client import PupClient

logger = logging.getLogger("pup-debug")

# This is the app uvicorn serves
app = create_app()

# --- TEMP: ask PupClient what it sees ---
client = PupClient.from_env()
logger.warning(
    "PUPCLIENT ENV CHECK demo_mode=%s api_key_set=%s base_url=%s",
    getattr(client, "demo_mode", None),
    bool(getattr(client, "api_key", None)),
    getattr(client, "base_url", None),
)

@app.get("/debug/env")
async def debug_env():
    return {
        # What Hugging Face injected
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),

        # What PupClient sees
        "client_demo_mode": getattr(client, "demo_mode", None),
        "client_has_api_key": bool(getattr(client, "api_key", None)),
        "client_base_url": getattr(client, "base_url", None),
    }
