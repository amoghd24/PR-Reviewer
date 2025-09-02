"""MCP Connection Manager for session lifecycle management."""

from typing import Dict, Optional
from fastmcp import Client
from .transports import create_stdio_transport, create_http_transport
from utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages MCP client connections and sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, Client] = {}
    
    async def connect(self, name: str, command: str, args: Optional[list] = None,
                     base_url: Optional[str] = None, headers: Optional[Dict[str, str]] = None) -> Client:
        """Create and establish a persistent session."""
        if name in self._sessions:
            return self._sessions[name]
        
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
        return client
    
    def get_session(self, name: str) -> Optional[Client]:
        """Get existing session by name."""
        return self._sessions.get(name)
    
    async def disconnect(self, name: str):
        """Close specific session."""
        if session := self._sessions.get(name):
            try:
                await session.__aexit__(None, None, None)
                del self._sessions[name]
            except Exception as e:
                logger.warning(f"Error closing {name}: {e}")
    
    async def disconnect_all(self):
        """Close all sessions."""
        for name in list(self._sessions.keys()):
            await self.disconnect(name)
    
    def is_connected(self, name: str) -> bool:
        """Check if session exists."""
        return name in self._sessions