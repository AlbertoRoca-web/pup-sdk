# app.py at repo root

import os
from pup_sdk.web.app import create_app

# Create the Alberto web interface app from the SDK
app = create_app()

# Optional debug endpoint to confirm env vars in the Space
@app.get("/debug/env")
async def debug_env():
    return {
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),
    }
