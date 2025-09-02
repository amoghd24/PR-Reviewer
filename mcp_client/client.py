"""Core MCP Client with session-based architecture."""

from typing import Dict, Any, Optional
from fastmcp import Client
from .transports import create_stdio_transport, create_http_transport
from utils.logger import get_logger

logger = get_logger(__name__)


class MCPClient:
    """Session-based MCP client following Anthropic guidelines."""
    
    def __init__(self):
        self._sessions: Dict[str, Client] = {}
    
    async def connect(self, name: str, command: str, args: Optional[list] = None, 
                     base_url: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """Connect and establish persistent session."""
        if name in self._sessions:
            return
        
        logger.info(f"Connecting to {name}")
        
        # Create transport based on parameters
        if base_url:
            transport = create_http_transport(base_url, headers)
        else:
            transport = create_stdio_transport(command, args or [])
        
        # Create and connect session
        client = Client(transport)
        await client.__aenter__()
        self._sessions[name] = client
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Optional[Dict[str, Any]] = None):
        """Call tool using persistent session."""
        session = self._sessions.get(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        result = await session.call_tool(tool_name, arguments or {})
        return result.content
    
    async def list_tools(self, server_name: str):
        """List tools using persistent session."""
        session = self._sessions.get(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        return await session.list_tools()
    
    async def list_prompts(self, server_name: str):
        """List prompts using persistent session."""
        session = self._sessions.get(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        result = await session.list_prompts()
        return result
    
    async def get_prompt(self, server_name: str, prompt_name: str, arguments: Optional[Dict[str, Any]] = None):
        """Get prompt with arguments using persistent session.""" 
        session = self._sessions.get(server_name)
        if not session:
            raise RuntimeError(f"Server {server_name} not connected")
        
        result = await session.get_prompt(prompt_name, arguments or {})
        return result.messages
    
    async def cleanup(self):
        """Close all sessions."""
        for name, session in self._sessions.items():
            try:
                await session.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing {name}: {e}")
        self._sessions.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()