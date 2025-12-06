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
    """Manage app lifecycle - create PupClient from environment on startup."""
    global _pup_client
    
    # Create client from environment variables (secure, no logging)
    try:
        _pup_client = PupClient.from_env()
        app.state.client = _pup_client
        
        if _pup_client.demo_mode:
            print("🐕 Alberto running in demo mode - no API key configured")
        else:
            print("🐕 Alberto client created with API key")
            # In HuggingFace Space mode, we don't connect to external Alberto server
            # The web app itself acts as the Alberto interface
            alberto_url = os.environ.get("ALBERTO_API_URL")
            if alberto_url:
                # Only connect if we have an external Alberto server URL
                _pup_client.base_url = alberto_url.rstrip("/")
                await _pup_client.connect()
                # Test the connection separately
                if await _pup_client.test_connection():
                    print("🐕 Alberto connected to external server successfully!")
                else:
                    print("⚠️ Alberto client created but external server unreachable")
            else:
                print("🐕 Alberto running in direct LLM mode (no external server)")
        yield
    except Exception as e:
        print(f"❌ Failed to initialize Alberto client: {e}")
        app.state.client = None
        yield
    finally:
        if _pup_client and _pup_client._session:
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
        client = getattr(app.state, 'client', None)
        connected = client and client.is_connected and not client.demo_mode
        demo_mode = not client or client.demo_mode
        
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
        """Handle chat requests."""
        client = getattr(app.state, 'client', None)
        
        if not client or client.demo_mode:
            # Demo mode response
            demo_responses = [
                "🐕 Woof! Alberto is currently running in demo mode. This is a simulated response!",
                "🐕 Hey there! In demo mode, I can still chat! To connect to the real Alberto, configure API keys!",
                "🐕 Demo mode activated! I'm giving sample responses. Real Alberto needs API keys to help with actual coding tasks.",
                "🐕 Hi! I'm Alberto's demo mode. The real me can help with coding, file operations, and more when API keys are configured!",
            ]
            
            import random
            response = random.choice(demo_responses)
            
            return ChatResponse(
                success=True,
                response=response,
                execution_time=0.1,
            )
            
        try:
            response = await client.chat(
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
        client = getattr(app.state, 'client', None)
        
        if not client:
            return {
                "available": False,
                "version": "0.1.0",
                "connected": False,
                "demo_mode": True,
                "message": "No client available"
            }
            
        try:
            status = await client.get_status()
            result = status.model_dump()
            # Add connection info
            result.update({
                "connected": client.is_connected,
                "demo_mode": client.demo_mode
            })
            return result
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "connected": client.is_connected,
                "demo_mode": client.demo_mode,
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