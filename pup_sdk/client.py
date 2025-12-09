"""Main client for interacting with Alberto."""

import asyncio
import json
import logging
import os
import socket
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import aiohttp
from aiohttp import resolver
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


def _parse_resolve_overrides(raw: Optional[str]) -> Dict[str, str]:
    if not raw:
        return {}
    overrides: Dict[str, str] = {}
    for chunk in raw.split(","):
        if "=" not in chunk:
            continue
        host, ip = chunk.split("=", 1)
        host = host.strip()
        ip = ip.strip()
        if host and ip:
            overrides[host] = ip
    return overrides


class StaticResolver(resolver.AbstractResolver):
    """Resolver that injects manual host→IP overrides before falling back."""

    def __init__(self, overrides: Optional[Dict[str, str]] = None):
        self._overrides = overrides or {}
        self._fallback = resolver.DefaultResolver()

    async def resolve(self, host, port=0, family=socket.AF_INET):
        override = self._overrides.get(host)
        if override:
            return [
                {
                    "hostname": host,
                    "host": override,
                    "port": port,
                    "family": socket.AF_INET,
                    "proto": 0,
                    "flags": 0,
                }
            ]
        return await self._fallback.resolve(host, port, family)

    async def close(self):
        await self._fallback.close()


class PupClient:
    """Async client for interacting with Alberto the code puppy."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: int = 60,
        demo_mode: bool = False,
    ):
        # Normalize base URL by stripping trailing slash
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        self._resolver_overrides = _parse_resolve_overrides(
            os.environ.get("PUP_RESOLVE_OVERRIDES"))
        self._resolver: Optional[StaticResolver] = None
        self._status_cache: Optional[PupStatus] = None
        self._cache_timestamp: Optional[datetime] = None
        self.demo_mode = demo_mode

        # Optional Cloudflare Access support:
        # - PUP_CF_ACCESS_JWT: raw JWT to send as CF-Access-Jwt-Assertion
        # - PUP_CF_ACCESS_CLIENT_ID / PUP_CF_ACCESS_CLIENT_SECRET: service token pair
        self._cf_access_jwt: Optional[str] = os.environ.get("PUP_CF_ACCESS_JWT")
        self._cf_client_id: Optional[str] = os.environ.get("PUP_CF_ACCESS_CLIENT_ID")
        self._cf_client_secret: Optional[str] = os.environ.get(
            "PUP_CF_ACCESS_CLIENT_SECRET"
        )

        # "Connected" just means we opened an HTTP session successfully.
        self._is_connected: bool = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_headers(self) -> Dict[str, str]:
        """
        Build the base headers for all HTTP requests.

        Includes:
        - JSON content type
        - Authorization: Bearer <api_key>  (if api_key is set)
        - Cloudflare Access headers (JWT or service token) when configured
        """
        headers: Dict[str, str] = {"Content-Type": "application/json"}

        # Core API auth – used only when talking directly to a provider.
        # When calling a remote Pup backend (Cloudflare Worker, etc.),
        # self.api_key is normally None.
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Cloudflare Access (JWT)
        if self._cf_access_jwt:
            headers["CF-Access-Jwt-Assertion"] = self._cf_access_jwt

        # Cloudflare Access (service token)
        if self._cf_client_id and self._cf_client_secret:
            headers["CF-Access-Client-Id"] = self._cf_client_id
            headers["CF-Access-Client-Secret"] = self._cf_client_secret

        return headers

    # ------------------------------------------------------------------
    # Context-manager lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Initialize the HTTP session - minimal and idempotent."""
        # Nothing to do if already connected
        if self._session is not None:
            return

        headers = self._build_headers()

        self._resolver = StaticResolver(self._resolver_overrides)

        connector = aiohttp.TCPConnector(resolver=self._resolver)

        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
            connector=connector,
        )

        self._is_connected = True

        has_cf = bool(
            self._cf_access_jwt
            or (self._cf_client_id and self._cf_client_secret)
        )
        logger.info(
            "🐕 Connected client session for Alberto at %s (Cloudflare Access=%s)",
            self.base_url,
            "on" if has_cf else "off",
        )

    async def test_connection(self) -> bool:
        """Test the connection with a lightweight check (no recursion)."""
        if self._session is None:
            return False

        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as test_session:
                headers = self._build_headers()
                async with test_session.get(
                    f"{self.base_url}/health",
                    headers=headers,
                ) as response:
                    success = response.status == 200
                    if success:
                        logger.info(
                            "🐕 Connection test successful for Alberto at %s",
                            self.base_url,
                        )
                    else:
                        logger.warning(
                            "🐕 Connection test failed: HTTP %s",
                            response.status,
                        )
                    return success
        except Exception as e:
            logger.warning("🐕 Connection test failed: %s", e)
            return False

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
            self._is_connected = False
            logger.info("🐕 Disconnected from Alberto")
        if self._resolver:
            await self._resolver.close()
            self._resolver = None

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected (session open and not marked disconnected)."""
        return self._is_connected and self._session is not None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the HTTP session, raising error if not connected."""
        if self._session is None:
            raise PupConnectionError("Not connected to Alberto. Call connect() first.")
        return self._session

    # ------------------------------------------------------------------
    # Core request helper
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to Alberto's API."""
        url = f"/api/v1{endpoint}"

        try:
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

                # Parse JSON, or raise a helpful error if it isn't JSON
                try:
                    response_data = await response.json()
                except Exception as e:
                    text = await response.text()
                    raise PupError(
                        f"Non-JSON response from backend (status={response.status}): {text}"
                    ) from e

                if response.status >= 400:
                    error_msg = response_data.get("error", "Unknown error")
                    raise PupError(error_msg)

                return response_data

        except asyncio.TimeoutError:
            raise PupTimeoutError(f"Request to {url} timed out")
        except aiohttp.ClientError as e:
            raise PupConnectionError(f"Connection error: {e}")

    # ------------------------------------------------------------------
    # Status and health methods
    # ------------------------------------------------------------------

    async def get_status(self) -> PupStatus:
        """Get Alberto's current status (cached for 30 seconds)."""
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

    # ------------------------------------------------------------------
    # Chat methods
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # File operation methods
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Shell command methods
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Agent methods
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    async def create_and_connect(
        cls,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ) -> "PupClient":
        """
        Create and connect a client instance.

        Order of precedence for the backend URL:
        1. ALBERTO_API_URL environment variable (Hugging Face / cloud).
        2. PUP_BACKEND_URL environment variable (optional legacy name).
        3. base_url argument.
        4. Default http://localhost:8080
        """
        backend_url = (
            os.environ.get("ALBERTO_API_URL")
            or os.environ.get("PUP_BACKEND_URL")
            or base_url
            or "http://localhost:8080"
        )

        if os.environ.get("PUP_RESOLVE_OVERRIDES"):
            logger.info(
                "Using manual DNS override(s): %s",
                os.environ.get("PUP_RESOLVE_OVERRIDES"),
            )

        if os.environ.get("PUP_RESOLVE_OVERRIDES"):
            logger.info(
                "Using manual DNS override(s): %s",
                os.environ.get("PUP_RESOLVE_OVERRIDES"),
            )

        # If a remote Pup backend URL is provided, treat it as authoritative:
        # the backend (e.g. Cloudflare Worker) holds the provider keys.
        if os.environ.get("ALBERTO_API_URL") or os.environ.get("PUP_BACKEND_URL"):
            client = cls(
                base_url=backend_url,
                api_key=None,
                timeout=timeout,
                demo_mode=False,
            )
            await client.connect()
            return client

        # Otherwise fall back to direct provider mode.
        if not api_key:
            syn_key = os.environ.get("SYN_API_KEY")
            openai_key = os.environ.get("OPEN_API_KEY")

            syn_key_valid = syn_key and syn_key.strip()
            openai_key_valid = openai_key and openai_key.strip()

            if syn_key_valid:
                api_key = syn_key
                logger.info("Using Syn provider")
            elif openai_key_valid:
                api_key = openai_key
                logger.info("Using OpenAI provider")
            else:
                raise ValueError(
                    "No model API key configured. "
                    "Set SYN_API_KEY or OPEN_API_KEY environment variable."
                )

        client = cls(
            base_url=backend_url,
            api_key=api_key,
            timeout=timeout,
            demo_mode=False,
        )
        await client.connect()
        return client

    @classmethod
    def from_env(
        cls,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ) -> "PupClient":
        """
        Create client instance from environment variables (secure, no logging).

        Order of precedence for the backend URL:
        1. ALBERTO_API_URL environment variable (Hugging Face / cloud).
        2. PUP_BACKEND_URL environment variable (optional legacy name).
        3. base_url argument.
        4. Default http://localhost:8080

        There are two broad modes:

        1) Remote Pup backend (Cloudflare Worker, bridge server, etc.).
           - Triggered when ALBERTO_API_URL/PUP_BACKEND_URL is set or when a
             non-local backend URL is provided with PUP_ALLOW_KEYLESS_BACKEND.
           - The worker/bridge owns the provider keys, so this client does not
             need OPEN_API_KEY/SYN_API_KEY and demo_mode stays False.

        2) Direct provider mode (no remote backend URL):
           - Uses SYN_API_KEY / OPEN_API_KEY to call providers directly.
           - demo_mode=True only when no valid keys are present.
        """
        backend_url = (
            os.environ.get("ALBERTO_API_URL")
            or os.environ.get("PUP_BACKEND_URL")
            or base_url
            or "http://localhost:8080"
        )

        if os.environ.get("PUP_RESOLVE_OVERRIDES"):
            logger.info(
                "Using manual DNS override(s): %s",
                os.environ.get("PUP_RESOLVE_OVERRIDES"),
            )

        if os.environ.get("PUP_RESOLVE_OVERRIDES"):
            logger.info(
                "Using manual DNS override(s): %s",
                os.environ.get("PUP_RESOLVE_OVERRIDES"),
            )

        # --- Mode 1: Remote Pup backend ---------------------------------
        if os.environ.get("ALBERTO_API_URL") or os.environ.get("PUP_BACKEND_URL"):
            return cls(
                base_url=backend_url,
                api_key=None,
                timeout=timeout,
                demo_mode=False,
            )

        # --- Mode 2: Direct provider ------------------------------------
        syn_key = os.environ.get("SYN_API_KEY")
        openai_key = os.environ.get("OPEN_API_KEY")
        provider_pref = (os.environ.get("PUP_PROVIDER") or "").lower()

        has_syn_key = syn_key and syn_key.strip()
        has_openai_key = openai_key and openai_key.strip()

        chosen_key: Optional[str] = None
        if provider_pref == "syn" and has_syn_key:
            chosen_key = syn_key
        elif provider_pref == "openai" and has_openai_key:
            chosen_key = openai_key
        elif has_openai_key:
            chosen_key = openai_key
        elif has_syn_key:
            chosen_key = syn_key

        if chosen_key:
            return cls(
                base_url=backend_url,
                api_key=chosen_key,
                timeout=timeout,
                demo_mode=False,
            )

        local_prefixes = (
            "http://localhost",
            "http://127.0.0.1",
            "https://localhost",
            "https://127.0.0.1",
        )
        backend_is_local = backend_url.startswith(local_prefixes)
        allow_keyless_backend = (
            not backend_is_local
            or (os.environ.get("PUP_ALLOW_KEYLESS_BACKEND") or "")
            .strip()
            .lower()
            in {"1", "true", "yes", "on"}
        )

        if allow_keyless_backend:
            return cls(
                base_url=backend_url,
                api_key=None,
                timeout=timeout,
                demo_mode=False,
            )

        # Demo mode when running locally with no API keys configured
        return cls(
            base_url=backend_url,
            api_key=None,
            timeout=timeout,
            demo_mode=True,
        )
