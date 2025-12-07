# app.py at repo root

import os
from pup_sdk.web.app import create_app

# Create the Alberto web interface app from the SDK
app = create_app()

# --- OPTIONAL: tiny debug endpoint for env vars ---
# You can remove this once things work.
@app.get("/debug/env")
def debug_env():
    return {
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),
    }
