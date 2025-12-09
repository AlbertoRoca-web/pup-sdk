"""FastAPI web application for Pup SDK.

Note on HTTP Status Codes:
- HTTP 304 (Not Modified) for static assets is normal cache revalidation
- HTTP 202 (Accepted) for /api/event, /telemetry, /metrics are HuggingFace analytics, not our app
- Only 4xx/5xx on our endpoints (/api/status, /api/chat, /static/style.css) indicate real problems
- 202/304 responses are expected behavior and should NOT be "fixed" in code
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from ..client import PupClient
from ..exceptions import PupError, PupConnectionError, PupTimeoutError
from ..types import ChatRequest, ChatResponse

# Global client instance, used for /api/capabilities, /api/agents, /health
_pup_client: Optional[PupClient] = None

_TRUE_VALUES = {"1", "true", "yes", "on"}
_LOCAL_PREFIXES = (
    "http://localhost",
    "http://127.0.0.1",
    "https://localhost",
    "https://127.0.0.1",
)


def _remote_backend_url() -> Optional[str]:
    return os.environ.get("ALBERTO_API_URL") or os.environ.get("PUP_BACKEND_URL")


def _force_live_backend() -> bool:
    url = _remote_backend_url()
    if not url:
        return False
    allow_keyless = not url.startswith(_LOCAL_PREFIXES)
    if not allow_keyless:
        flag = (os.environ.get("PUP_ALLOW_KEYLESS_BACKEND") or "").strip().lower()
        allow_keyless = flag in _TRUE_VALUES
    return allow_keyless




def _ensure_live_client(app: FastAPI) -> Optional[PupClient]:
    """Ensure we have a live client when a remote backend is configured."""
    client: Optional[PupClient] = getattr(app.state, "client", None)
    remote_url = _remote_backend_url()
    force_live = _force_live_backend()

    if not force_live:
        return client

    normalized_remote = (remote_url or "").rstrip("/")
    needs_refresh = (
        client is None
        or client.demo_mode
        or client.base_url.rstrip("/") != normalized_remote
    )

    if not needs_refresh:
        return client

    try:
        print("🔁 Refreshing PupClient for remote backend")
        refreshed = PupClient.from_env(base_url=remote_url)
        app.state.client = refreshed
        global _pup_client
        _pup_client = refreshed
        return refreshed
    except Exception as exc:
        print(f"⚠️ Failed to refresh PupClient for remote backend: {exc}")
        return client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - create/reuse PupClient and connect on startup."""
    global _pup_client

    try:
        # Reuse client if create_app() injected one, otherwise build from env.
        client = getattr(app.state, "client", None)
        if client is None:
            client = PupClient.from_env()
            app.state.client = client

        client = _ensure_live_client(app) or client
        _pup_client = client

        force_live = _force_live_backend()

        if client.demo_mode and force_live:
            print("⚙️ Remote backend detected; forcing live mode even though PupClient reported demo.")
            client.demo_mode = False

        if client.demo_mode:
            print("🐕 Alberto running in demo mode - no API key configured")
        else:
            if getattr(client, "api_key", None):
                print("🐕 Alberto client created with API key")
            else:
                print("🐕 Alberto client created without API key (keyless backend)")
            print(f"🔗 Alberto backend URL: {client.base_url}")
            try:
                await client.connect()
                print("🐕 Alberto client connected successfully!")
            except Exception as connect_error:
                print(f"⚠️ Failed to connect Alberto client: {connect_error}")
                client._is_connected = False
                if not force_live:
                    client.demo_mode = True
                    print("🔄 Falling back to demo mode due to connection failure")
                else:
                    print(
                        "🔁 Remote backend configured; staying in live mode and will retry per request."
                    )

        # Hand control back to FastAPI
        yield

    except Exception as e:
        print(f"❌ Failed to initialize Alberto client: {e}")
        app.state.client = None
        _pup_client = None
        yield
    finally:
        if _pup_client and getattr(_pup_client, "_session", None):
            await _pup_client.close()
            print("🐕 Alberto disconnected")


def create_app(client: Optional[PupClient] = None) -> FastAPI:
    """Create the FastAPI application.

    If a PupClient is provided, it will be used and managed by the lifespan
    context. Otherwise, a new PupClient will be constructed from the environment.
    """

    app = FastAPI(
        title="Alberto - Code Puppy Web Interface",
        description="Mobile-friendly web interface for Alberto the code puppy",
        version="0.1.0",
        lifespan=lifespan,
    )

    # If an external client was passed in (e.g., from root app.py), store it.
    if client is not None:
        app.state.client = client

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="pup_sdk/web/static"), name="static")

    # Templates
    templates = Jinja2Templates(directory="pup_sdk/web/templates")

    async def _run_demo_chat(request: ChatRequest) -> ChatResponse:
        """Helper function for demo mode chat responses."""
        demo_responses: List[str] = [
            "🐕 Woof! Alberto is currently running in demo mode. This is a simulated response!",
            "🐕 Hey there! In demo mode, I can still chat! To connect to the real Alberto, configure API keys!",
            "🐕 Demo mode activated! I'm giving sample responses. Real Alberto needs API keys to help with actual coding tasks.",
            "🐕 Hi! I'm Alberto's demo mode. The real me can help with coding, file operations, and more when API keys are configured!",
        ]

        import random

        response_text = random.choice(demo_responses)
        return ChatResponse(
            success=True,
            response=response_text,
            execution_time=0.1,
        )

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """Serve the main web interface."""
        client = _ensure_live_client(app)
        force_live = _force_live_backend()
        demo_mode = not client or (client.demo_mode and not force_live)
        connected = bool(client and client.is_connected and not demo_mode)

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Alberto - Your Code Puppy!",
                "connected": connected,
                "demo_mode": demo_mode,
            },
        )

    @app.post("/api/chat")
    async def chat_endpoint(request: ChatRequest):
        """Handle chat requests with demo fallback on all failures."""
        client: Optional[PupClient] = _ensure_live_client(app)
        force_live = _force_live_backend()

        if not client:
            return await _run_demo_chat(request)

        if force_live and client.demo_mode:
            client.demo_mode = False

        # (a) if demo mode (and no forced backend) return demo chat
        if not force_live and client.demo_mode:
            return await _run_demo_chat(request)

        # (b) ensure connection
        if not client.is_connected:
            try:
                await client.connect()
            except Exception as exc:
                client._is_connected = False
                if not force_live:
                    client.demo_mode = True
                print(f"Chat connect failed: {exc}")
                return await _run_demo_chat(request)

        # (c) try live chat, fallback to demo on any exception
        try:
            response = await client.chat(
                message=request.message,
                context=request.context,
                include_reasoning=request.include_reasoning,
                auto_execute=request.auto_execute,
            )
            return response
        except (PupTimeoutError, PupConnectionError, PupError, Exception) as e:
            print(f"Chat failed, falling back to demo: {type(e).__name__}: {e}")
            client._is_connected = False
            if not force_live:
                client.demo_mode = True
            return await _run_demo_chat(request)

    @app.get("/api/status")
    async def status_endpoint():
        """Get Alberto's status with proper demo fallback."""
        client: Optional[PupClient] = _ensure_live_client(app)
        force_live = _force_live_backend()

        # (a) if client is None, return demo mode response
        if not client:
            return {
                "available": False,
                "version": "0.1.0",
                "connected": False,
                "demo_mode": not force_live,
                "message": "No client available",
            }

        if force_live and client.demo_mode:
            client.demo_mode = False

        # (b) if client.demo_mode is True and no forced backend, return immediate demo response
        if client.demo_mode and not force_live:
            return {
                "available": True,
                "version": "0.1.0",
                "connected": False,
                "demo_mode": True,
                "message": "Running in demo mode",
            }

        # (c) if not client.is_connected, try to connect and fallback appropriately
        if not client.is_connected:
            try:
                await client.connect()
            except Exception as exc:
                client._is_connected = False
                if not force_live:
                    client.demo_mode = True
                    return {
                        "available": False,
                        "version": "0.1.0",
                        "connected": False,
                        "demo_mode": True,
                        "error": "connection_failed",
                    }
                return {
                    "available": False,
                    "version": "0.1.0",
                    "connected": False,
                    "demo_mode": False,
                    "error": f"connection_failed: {exc}",
                }

        # (d) try to get status, fallback appropriately
        try:
            status = await client.get_status()
            result = status.model_dump()
            result.update(
                {
                    "connected": client.is_connected and not client.demo_mode,
                    "demo_mode": client.demo_mode and not force_live,
                }
            )
            return result
        except Exception as exc:
            client._is_connected = False
            if not force_live:
                client.demo_mode = True
                return {
                    "available": False,
                    "version": "0.1.0",
                    "connected": False,
                    "demo_mode": True,
                    "error": "connection_failed",
                }
            return {
                "available": False,
                "version": "0.1.0",
                "connected": False,
                "demo_mode": False,
                "error": f"connection_failed: {exc}",
            }

    @app.get("/api/capabilities")
    async def capabilities_endpoint():
        """Get Alberto's capabilities."""
        global _pup_client

        if not _pup_client:
            return ["chat", "demo_mode"]

        try:
            capabilities = await _pup_client.get_capabilities()
            return capabilities
        except Exception:
            return ["chat"]

    @app.get("/api/agents")
    async def agents_endpoint():
        """List available agents."""
        global _pup_client

        if not _pup_client:
            return []

        try:
            agents = await _pup_client.list_agents()
            return agents
        except Exception:
            return []

    @app.get("/health")
    async def health_check():
        """Simple health check endpoint."""
        global _pup_client

        if _pup_client:
            try:
                healthy = await _pup_client.health_check()
                return {"status": "healthy" if healthy else "unhealthy"}
            except Exception:
                return {"status": "error"}
        return {"status": "demo_mode"}

    return app


def launch_web(
    host: str = "0.0.0.0",
    port: int = 7860,
    reload: bool = False,
    log_level: str = "info",
) -> None:
    """Launch the web interface (for local/dev usage)."""
    app = create_app()

    print(f"🌐 Starting Alberto Web Interface on http://{host}:{port}")
    print("📱 Mobile-friendly interface ready!")
    print("🌐 HuggingFace Spaces compatible!")

    # Show environment info for debugging
    alberto_url = os.environ.get("ALBERTO_API_URL") or os.environ.get(
        "PUP_BACKEND_URL"
    ) or "http://localhost:8080"
    print(f"🔗 Alberto endpoint: {alberto_url}")

    uvicorn.run(
        app,  # Direct app object instead of string reference
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    # Read from environment for HuggingFace Spaces compatibility
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")

    launch_web(host=host, port=port)
