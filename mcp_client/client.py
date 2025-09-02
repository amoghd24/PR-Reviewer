"""Core MCP Client with session-based architecture."""

from typing import Dict, Any, Optional
from .connection_manager import ConnectionManager
from utils.logger import get_logger

logger = get_logger(__name__)


class MCPClient:
    """Session-based MCP client following Anthropic guidelines."""
    
    def __init__(self):
        self._connection_manager = ConnectionManager()
    
    async def connect(self, name: str, command: str, args: Optional[list] = None, 
                     base_url: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """Connect and establish persistent session."""
        await self._connection_manager.connect(name, command, args, base_url, headers)
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Optional[Dict[str, Any]] = None):
        """Call tool using persistent session."""
        session = self._connection_manager.get_session(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        result = await session.call_tool(tool_name, arguments or {})
        return result.content
    
    async def list_tools(self, server_name: str):
        """List tools using persistent session."""
        session = self._connection_manager.get_session(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        return await session.list_tools()
    
    async def list_prompts(self, server_name: str):
        """List prompts using persistent session."""
        session = self._connection_manager.get_session(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        result = await session.list_prompts()
        return result
    
    async def get_prompt(self, server_name: str, prompt_name: str, arguments: Optional[Dict[str, Any]] = None):
        """Get prompt with arguments using persistent session.""" 
        session = self._connection_manager.get_session(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        result = await session.get_prompt(prompt_name, arguments or {})
        return result.messages
    
    async def cleanup(self):
        """Close all sessions."""
        await self._connection_manager.disconnect_all()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()