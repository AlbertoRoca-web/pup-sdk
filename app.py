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
    "PUPCLIENT ENV CHECK demo_mode=%s open_key=%s syn_key=%s",
    getattr(client, "demo_mode", None),
    bool(getattr(client, "open_api_key", None)),
    bool(getattr(client, "syn_api_key", None)),
)

@app.get("/debug/env")
async def debug_env():
    return {
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),
    }
