# app.py at repo root
import os
from pup_sdk.web.app import create_app

app = create_app()

@app.get("/debug/env")
def debug_env():
    return {
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
    }
