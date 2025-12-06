"""HuggingFace Spaces app for Alberto."""

import os
from pup_sdk.web import launch_web

if __name__ == "__main__":
    # Read PORT from environment for HuggingFace Spaces compatibility
    port = int(os.environ.get("PORT", 7860))
    
    # Launch with HuggingFace Spaces defaults
    launch_web(host="0.0.0.0", port=port)