"""HuggingFace Spaces app for Alberto."""

from pup_sdk.web import launch_web

if __name__ == "__main__":
    # Launch with HuggingFace Spaces defaults
    launch_web(host="0.0.0.0", port=7860)