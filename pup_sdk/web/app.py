"""FastAPI web application for Pup SDK."""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from ..client import PupClient
from ..exceptions import PupError, PupConnectionError, PupTimeoutError
from ..types import ChatRequest, ChatResponse
from .templates import get_template

# Global client instance
_pup_client: Optional[PupClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - connect to Alberto on startup."""
    global _pup_client
    
    try:
        # Connect to Alberto
        _pup_client = PupClient()
        await _pup_client.connect()
        print("\ud83d\dc15 Alberto connected for web interface!")
        yield
    except Exception as e:
        print(f"\u274c Failed to connect to Alberto: {e}")
        print("Running in demo mode - responses will be simulated")
        yield
    finally:
        if _pup_client:
            await _pup_client.close()
            print("\ud83d\dc15 Alberto disconnected")


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    
    app = FastAPI(
        title="Alberto - Code Puppy Web Interface",
        description="Mobile-friendly web interface for Alberto the code puppy",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Templates
    templates = Jinja2Templates(directory="pup_sdk/web/templates")
    
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """Serve the main web interface."""
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Alberto - Your Code Puppy!",
                "connected": _pup_client is not None,
            },
        )
        
    @app.post("/api/chat")
    async def chat_endpoint(request: ChatRequest):
        """Handle chat requests."""
        if not _pup_client:
            # Demo mode response
            return ChatResponse(
                success=True,
                response=(
                    "\ud83d\dc15 Woof! Alberto is currently offline in demo mode. "
                    "This is a simulated response. To connect to the real Alberto, "
                    "make sure the code-puppy agent is running on localhost:8080!"
                ),
                execution_time=0.1,
            )
            
        try:
            response = await _pup_client.chat(
                message=request.message,
                context=request.context,
                include_reasoning=request.include_reasoning,
                auto_execute=request.auto_execute,
            )
            return response
        except PupTimeoutError:
            raise HTTPException(status_code=408, detail="Request timeout")
        except PupConnectionError:
            raise HTTPException(status_code=503, detail="Alberto is unavailable")
        except PupError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    @app.get("/api/status")
    async def status_endpoint():
        """Get Alberto's status."""
        if not _pup_client:
            return {
                "available": False,
                "version": "0.1.0 (demo mode)",
                "connected": False,
            }
            
        try:
            status = await _pup_client.get_status()
            return status.model_dump()
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "connected": False,
            }
            
    @app.get("/api/capabilities")
    async def capabilities_endpoint():
        """Get Alberto's capabilities."""
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
        if _pup_client:
            try:
                healthy = await _pup_client.health_check()
                return {"status": "healthy" if healthy else "unhealthy"}
            except:
                return {"status": "error"}
        return {"status": "demo_mode"}
        
    return app


def launch_web(
    host: str = "0.0.0.0",
    port: int = 7860,
    reload: bool = False,
    log_level: str = "info",
) -> None:
    """Launch the web interface."""
    app = create_app()
    
    print(f"\ud83d\dce1 Starting Alberto Web Interface on http://{host}:{port}")
    print("📱 Mobile-friendly interface ready!")
    print("🌐 HuggingFace Spaces compatible!")
    
    uvicorn.run(
        "pup_sdk.web.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    launch_web()