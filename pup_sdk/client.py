"""Main client for interacting with Alberto."""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import aiohttp
from pydantic import BaseModel

from .exceptions import (
    PupConnectionError,
    PupTimeoutError,
    PupValidationError,
    PupError,
)
from .types import (
    AgentRequest,
    AgentResponse,
    ChatRequest,
    ChatResponse,
    FileOperation,
    FileOperationResult,
    FileInfo,
    PupStatus,
    ShellCommand,
    ShellCommandResult,
    SearchResult,
)

logger = logging.getLogger(__name__)


class PupClient:
    """Async client for interacting with Alberto the code puppy."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: int = 60,
        demo_mode: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        self._status_cache: Optional[PupStatus] = None
        self._cache_timestamp: Optional[datetime] = None
        self.demo_mode = demo_mode
        self.is_connected = bool(api_key) and not demo_mode
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def connect(self) -> None:
        """Initialize the HTTP session."""
        if self._session is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            self._session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
            )
            
        # Mark as connected (no automatic status test to avoid recursion)
        logger.info(f"🐕 HTTP session created for Alberto at {self.base_url}")
        
    async def test_connection(self) -> bool:
        """Test the connection (separate from connect() to avoid recursion)."""
        try:
            await self.get_status()
            logger.info(f"🐕 Connection test successful for Alberto at {self.base_url}")
            return True
        except Exception as e:
            logger.warning(f"🐕 Connection test failed: {e}")
            return False
        
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
            logger.info("🐕 Disconnected from Alberto")
            
    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the HTTP session, raising error if not connected."""
        if self._session is None:
            raise PupConnectionError("Not connected to Alberto. Call connect() first.")
        return self._session
        
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to Alberto's API."""
        try:
            url = f"/api/v1{endpoint}"
            
            if isinstance(data, BaseModel):
                data = data.model_dump()
                
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
            ) as response:
                if response.status == 401:
                    raise PupConnectionError("Invalid API key")
                if response.status == 408:
                    raise PupTimeoutError("Request timeout")
                if response.status >= 500:
                    raise PupConnectionError(f"Server error: {response.status}")
                    
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = response_data.get("error", "Unknown error")
                    raise PupError(error_msg)
                    
                return response_data
                
        except asyncio.TimeoutError:
            raise PupTimeoutError(f"Request to {url} timed out")
        except aiohttp.ClientError as e:
            raise PupConnectionError(f"Connection error: {e}")
            
    # Status and health methods
    async def get_status(self) -> PupStatus:
        """Get Alberto's current status."""
        # Cache status for 30 seconds
        now = datetime.now()
        if (
            self._status_cache 
            and self._cache_timestamp 
            and (now - self._cache_timestamp).total_seconds() < 30
        ):
            return self._status_cache
            
        response = await self._request("GET", "/status")
        self._status_cache = PupStatus(**response)
        self._cache_timestamp = now
        return self._status_cache
        
    async def health_check(self) -> bool:
        """Check if Alberto is available."""
        try:
            status = await self.get_status()
            return status.available
        except Exception:
            return False
            
    # Chat methods
    async def say_woof(self, message: str, **kwargs) -> ChatResponse:
        """Send a message to Alberto and get a response."""
        request = ChatRequest(message=message, **kwargs)
        response = await self._request("POST", "/chat", data=request)
        return ChatResponse(**response)
        
    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        include_reasoning: bool = False,
        auto_execute: bool = False,
    ) -> ChatResponse:
        """Chat with Alberto (alias for say_woof)."""
        return await self.say_woof(
            message=message,
            context=context,
            include_reasoning=include_reasoning,
            auto_execute=auto_execute,
        )
        
    # File operation methods
    async def list_files(
        self,
        directory: str = ".",
        recursive: bool = True,
    ) -> List[FileInfo]:
        """List files in a directory."""
        operation = FileOperation(
            operation="list",
            directory=directory,
            recursive=recursive,
        )
        response = await self._request("POST", "/files", data=operation)
        result = FileOperationResult(**response)
        
        if not result.success:
            raise PupError(result.error or "File listing failed")
            
        return result.files or []
        
    async def read_file(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        num_lines: Optional[int] = None,
    ) -> str:
        """Read file contents."""
        operation = FileOperation(
            operation="read",
            file_path=file_path,
            start_line=start_line,
            num_lines=num_lines,
        )
        response = await self._request("POST", "/files", data=operation)
        result = FileOperationResult(**response)
        
        if not result.success:
            raise PupError(result.error or "File read failed")
            
        return result.content or ""
        
    async def write_file(
        self,
        file_path: str,
        content: str,
        overwrite: bool = False,
    ) -> bool:
        """Write content to a file."""
        operation = FileOperation(
            operation="write",
            file_path=file_path,
            content=content,
            overwrite=overwrite,
        )
        response = await self._request("POST", "/files", data=operation)
        result = FileOperationResult(**response)
        
        if not result.success:
            raise PupError(result.error or "File write failed")
            
        return True
        
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        operation = FileOperation(
            operation="delete",
            file_path=file_path,
        )
        response = await self._request("POST", "/files", data=operation)
        result = FileOperationResult(**response)
        
        if not result.success:
            raise PupError(result.error or "File deletion failed")
            
        return True
        
    async def search_files(
        self,
        search_string: str,
        directory: str = ".",
        max_results: int = 100,
    ) -> List[SearchResult]:
        """Search for text patterns in files."""
        params = {
            "q": search_string,
            "directory": directory,
            "max_results": max_results,
        }
        
        response = await self._request("GET", "/search", params=params)
        return [SearchResult(**item) for item in response.get("results", [])]
        
    # Shell command methods
    async def run_command(
        self,
        command: str,
        working_directory: Optional[str] = None,
        timeout: int = 60,
        capture_output: bool = True,
    ) -> ShellCommandResult:
        """Execute a shell command."""
        shell_cmd = ShellCommand(
            command=command,
            working_directory=working_directory,
            timeout=timeout,
            capture_output=capture_output,
        )
        response = await self._request("POST", "/shell", data=shell_cmd)
        return ShellCommandResult(**response)
        
    # Agent methods
    async def invoke_agent(
        self,
        agent_name: str,
        prompt: str,
        session_id: Optional[str] = None,
    ) -> AgentResponse:
        """Invoke a specific agent."""
        request = AgentRequest(
            agent_name=agent_name,
            prompt=prompt,
            session_id=session_id,
        )
        response = await self._request("POST", "/agents", data=request)
        return AgentResponse(**response)
        
    async def list_agents(self) -> List[str]:
        """List available agents."""
        response = await self._request("GET", "/agents")
        return response.get("agents", [])
        
    # Utility methods
    async def get_capabilities(self) -> List[str]:
        """Get list of Alberto's capabilities."""
        status = await self.get_status()
        return [cap.name for cap in status.capabilities if cap.enabled]
        
    async def wait_until_ready(self, timeout: int = 60) -> bool:
        """Wait until Alberto is ready."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if await self.health_check():
                return True
                
            if asyncio.get_event_loop().time() - start_time > timeout:
                return False
                
            await asyncio.sleep(1)
            
    @classmethod
    async def connect(
        cls,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ) -> "PupClient":
        """Create and connect a client instance."""
        # Read API keys from environment if not provided
        if not api_key:
            syn_key = os.environ.get("SYN_API_KEY")
            openai_key = os.environ.get("OPEN_API_KEY")
            
            if syn_key:
                api_key = syn_key
                logger.info("Using Syn provider")
            elif openai_key:
                api_key = openai_key
                logger.info("Using OpenAI provider")
            else:
                raise ValueError("No model API key configured. Set SYN_API_KEY or OPEN_API_KEY environment variable.")
        
        client = cls(base_url=base_url, api_key=api_key, timeout=timeout)
        await client.connect()
        return client
        
    @classmethod
    def from_env(
        cls,
        base_url: str = "http://localhost:8080",
        timeout: int = 60,
    ) -> "PupClient":
        """Create client instance from environment variables (secure, no logging)."""
        syn_key = os.environ.get("SYN_API_KEY")
        openai_key = os.environ.get("OPEN_API_KEY")
        
        # Check for valid keys (not empty strings)
        has_syn_key = syn_key and syn_key.strip()
        has_openai_key = openai_key and openai_key.strip()
        
        if has_syn_key:
            return cls(
                base_url=base_url,
                api_key=syn_key,
                timeout=timeout,
                demo_mode=False
            )
        elif has_openai_key:
            return cls(
                base_url=base_url,
                api_key=openai_key,
                timeout=timeout,
                demo_mode=False
            )
        else:
            # Demo mode when no keys available
            return cls(
                base_url=base_url,
                api_key=None,
                timeout=timeout,
                demo_mode=True
            )