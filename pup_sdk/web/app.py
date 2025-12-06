"""FastAPI web application for Pup SDK."""

import asyncio
import os
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

# Global client instance
_pup_client: Optional[PupClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - connect to Alberto on startup."""
    global _pup_client
    
    # Read configuration from environment variables
    alberto_url = os.environ.get("ALBERTO_API_URL", "http://localhost:8080")
    api_key = os.environ.get("ALBERTO_API_KEY")
    timeout = int(os.environ.get("ALBERTO_TIMEOUT", "60"))
    
    try:
        # Connect to Alberto
        _pup_client = PupClient(
            base_url=alberto_url,
            api_key=api_key,
            timeout=timeout
        )
        await _pup_client.connect()
        print(f"🐕 Alberto connected to {alberto_url}!")
        yield
    except Exception as e:
        print(f"❌ Failed to connect to Alberto: {e}")
        print("📡 Running in demo mode - responses will be simulated")
        print("💡 To connect to Alberto, run: python bridge_server.py")
        yield
    finally:
        if _pup_client:
            await _pup_client.close()
            print("🐕 Alberto disconnected")


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
            demo_responses = [
                "🐕 Woof! Alberto is currently running in demo mode. This is a simulated response!",
                "🐕 Hey there! In demo mode, I can still chat! To connect to the real Alberto, ask the admin to run the bridge server!",
                "🐕 Demo mode activated! I'm giving sample responses. Real Alberto needs the bridge server running to help with actual coding tasks.",
                "🐕 Hi! I'm Alberto's demo mode. The real me can help with coding, file operations, and more when the bridge server is connected!",
            ]
            
            import random
            response = random.choice(demo_responses)
            
            return ChatResponse(
                success=True,
                response=response,
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
                "message": "Bridge server not connected"
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
    
    print(f"🌐 Starting Alberto Web Interface on http://{host}:{port}")
    print("📱 Mobile-friendly interface ready!")
    print("🌐 HuggingFace Spaces compatible!")
    
    # Show environment info for debugging
    alberto_url = os.environ.get("ALBERTO_API_URL", "http://localhost:8080")
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