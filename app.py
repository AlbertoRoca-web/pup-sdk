# app.py at repo root: HuggingFace/uvicorn entrypoint for Alberto web UI

import os
from fastapi import FastAPI
from pup_sdk.web.app import create_app as create_pup_app

# Create the Alberto web interface from the SDK
pup_app = create_pup_app()

# Wrap in a top-level FastAPI app, so we can hang extra routes if we want
app = FastAPI()

# Mount the pup app at root so the existing UI keeps working at "/"
app.mount("/", pup_app)


# --- OPTIONAL: tiny debug endpoint for env vars ---
# Note: this is mounted on the *outer* app so it can't get swallowed
# by any internal routing tricks. You can remove this once things work.
@app.get("/debug/env", include_in_schema=False)
def debug_env():
    return {
        "has_OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "has_OPEN_API_KEY": bool(os.getenv("OPEN_API_KEY")),
        "has_SYN_API_KEY": bool(os.getenv("SYN_API_KEY")),
        "has_SYNTHETIC_API_KEY": bool(os.getenv("SYNTHETIC_API_KEY")),
        "has_HUGGINGPUP": bool(os.getenv("HUGGINGPUP")),
    }
