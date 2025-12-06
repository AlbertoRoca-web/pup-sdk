"""Type definitions for the Pup SDK."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """Information about a file or directory."""
    
    name: str
    path: str
    size: int
    is_file: bool
    is_directory: bool
    modified_time: Optional[datetime] = None
    permissions: Optional[str] = None


class SearchResult(BaseModel):
    """Search result from file grep operations."""
    
    file_path: str
    line_number: int
    line_content: str
    match_start: int
    match_end: int


class ShellCommand(BaseModel):
    """Shell command request."""
    
    command: str = Field(..., min_length=1, description="Command to execute")
    working_directory: Optional[str] = Field(None, description="Working directory")
    timeout: int = Field(60, ge=1, le=300, description="Timeout in seconds")
    capture_output: bool = Field(True, description="Whether to capture stdout/stderr")


class ShellCommandResult(BaseModel):
    """Result of shell command execution."""
    
    success: bool
    command: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time: float
    timeout: bool = False
    user_interrupted: bool = False


class FileOperation(BaseModel):
    """File operation request."""
    
    operation: str = Field(..., description="Type of operation: read, write, list, delete")
    file_path: Optional[str] = None
    directory: Optional[str] = None
    content: Optional[str] = None
    recursive: bool = Field(False, description="Whether to operate recursively")
    start_line: Optional[int] = Field(None, ge=1, description="Start line for read operations")
    num_lines: Optional[int] = Field(None, ge=1, description="Number of lines to read")
    overwrite: bool = Field(False, description="Whether to overwrite existing files")


class FileOperationResult(BaseModel):
    """Result of file operation."""
    
    success: bool
    operation: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    files: Optional[List[FileInfo]] = None
    num_tokens: Optional[int] = None
    error: Optional[str] = None


class AgentRequest(BaseModel):
    """Request to invoke an agent."""
    
    agent_name: str = Field(..., description="Name of the agent to invoke")
    prompt: str = Field(..., min_length=1, description="Prompt to send to agent")
    session_id: Optional[str] = Field(None, description="Session ID for conversation memory")


class AgentResponse(BaseModel):
    """Response from agent invocation."""
    
    success: bool
    agent_name: str
    response: str
    session_id: Optional[str] = None
    execution_time: float
    error: Optional[str] = None


class PupMessage(BaseModel):
    """Message to/from Alberto."""
    
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: str = Field("chat", description="Type: chat, command, response")
    metadata: Optional[Dict[str, Any]] = None


class PupCapability(BaseModel):
    """Description of Alberto's capabilities."""
    
    name: str
    description: str
    enabled: bool = True
    requires_auth: bool = False
    parameters: Optional[Dict[str, Any]] = None


class PupStatus(BaseModel):
    """Alberto's current status."""
    
    available: bool
    version: str
    uptime: Optional[float] = None
    current_directory: Optional[str] = None
    capabilities: List[PupCapability]
    last_activity: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request to Alberto."""
    
    message: str = Field(..., min_length=1, description="Message to send")
    context: Optional[Dict[str, Any]] = None
    include_reasoning: bool = Field(False, description="Whether to include reasoning")
    auto_execute: bool = Field(False, description="Whether to auto-execute commands")


class ChatResponse(BaseModel):
    """Chat response from Alberto."""
    
    success: bool
    response: str
    reasoning: Optional[str] = None
    commands_executed: List[Dict[str, Any]] = Field(default_factory=list)
    execution_time: float
    token_usage: Optional[Dict[str, int]] = None