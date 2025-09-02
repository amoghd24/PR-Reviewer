"""MCP Tool Wrapper for LangChain Integration."""

import asyncio
from typing import List, Dict, Any
from langchain.tools import Tool
from mcp_client import MCPClient
from utils.logger import get_logger

logger = get_logger(__name__)


class MCPToolWrapper:
    """Wrapper to expose MCP tools as LangChain tools."""
    
    def __init__(self):
        self.mcp_client = None
        self.connected = False
        
    async def initialize(self):
        """Initialize MCP client and connect to global server."""
        if self.connected:
            return
            
        self.mcp_client = MCPClient()
        
        # Connect to the global MCP server using uv
        await self.mcp_client.connect(
            name="global_registry",
            command="uv",
            args=["run", "python", "-m", "global_server.server"]
        )
        
        self.connected = True
        logger.info("Connected to global MCP registry")
    
    async def call_tool(self, tool_name: str, **kwargs) -> str:
        """Execute an MCP tool through the global registry."""
        if not self.connected:
            await self.initialize()
            
        try:
            result = await self.mcp_client.call_tool(
                server_name="global_registry",
                tool_name=tool_name,
                arguments=kwargs
            )
            return str(result)
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return f"Error: {str(e)}"
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from the global registry."""
        if not self.connected:
            await self.initialize()
            
        try:
            tools = await self.mcp_client.list_tools("global_registry")
            return tools
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []
    
    async def create_langchain_tools(self) -> List[Tool]:
        """Convert all MCP tools to LangChain Tools."""
        # Get MCP tools asynchronously
        mcp_tools = await self.get_available_tools()
        langchain_tools = []
        
        for tool_meta in mcp_tools:
            # Handle both dict and object formats
            if hasattr(tool_meta, 'name'):
                tool_name = tool_meta.name
                description = tool_meta.description if hasattr(tool_meta, 'description') else "No description available"
            else:
                tool_name = tool_meta.get("name", "unknown_tool")
                description = tool_meta.get("description", "No description available")
            
            # Create sync wrapper for each tool
            def make_tool_func(name):
                def tool_func(query: str = "", **kwargs):
                    # LangChain may pass a positional argument
                    # Use asyncio.run for sync wrapper
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        # If query is provided, add it to kwargs
                        if query:
                            kwargs['query'] = query
                        return loop.run_until_complete(self.call_tool(name, **kwargs))
                    finally:
                        loop.close()
                return tool_func
            
            langchain_tools.append(Tool(
                name=tool_name,
                description=description,
                func=make_tool_func(tool_name)
            ))
            
        logger.info(f"Created {len(langchain_tools)} LangChain tools from MCP")
        return langchain_tools
    
    async def cleanup(self):
        """Clean up MCP client connections."""
        if self.mcp_client and self.connected:
            await self.mcp_client.cleanup()
            self.connected = False