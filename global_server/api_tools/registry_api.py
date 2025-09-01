"""Registry API integration - FastMCP tool registration."""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from utils.logger import get_logger
from global_server.registry import McpServersRegistry
from .search_tools import search_tools_api, get_tools_by_tags_api
from .metadata_tools import get_tool_metadata_api, get_tools_by_server_api
from .analytics_tools import get_tag_statistics_api, get_popular_tools_api, record_tool_usage_api

logger = get_logger(__name__)


async def register_api_tools(app: FastMCP, registry: McpServersRegistry) -> None:
    """Register all registry API tools with the FastMCP app."""
    
    @app.tool(
        tags=["registry", "search", "tool-discovery"],
        description="Search for tools using advanced filters"
    )
    async def search_tools(
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        server_prefix: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for tools with multiple filters."""
        return await search_tools_api(registry, query, tags, server_prefix, limit)
    
    @app.tool(
        tags=["registry", "tools", "metadata"],
        description="Get metadata for a specific tool"
    )
    async def get_tool_metadata(tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for a specific tool."""
        return await get_tool_metadata_api(registry, tool_name)
    
    @app.tool(
        tags=["registry", "tags", "statistics"],
        description="Get statistics about available tags"
    )
    async def get_tag_statistics() -> Dict[str, int]:
        """Get usage statistics for all tags."""
        return await get_tag_statistics_api(registry)
    
    @app.tool(
        tags=["registry", "tools", "popular"],
        description="Get most frequently used tools"
    )
    async def get_popular_tools(limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently used tools."""
        return await get_popular_tools_api(registry, limit)
    
    @app.tool(
        tags=["registry", "servers", "tools"],
        description="Get all tools from a specific server"
    )
    async def get_tools_by_server(server_prefix: str) -> List[Dict[str, Any]]:
        """Get all tools from a specific server."""
        return await get_tools_by_server_api(registry, server_prefix)
    
    @app.tool(
        tags=["registry", "tags", "discovery"],
        description="Get tools that match multiple tags"
    )
    async def get_tools_by_tags(tags: List[str], match_all: bool = True) -> List[str]:
        """Get tools matching multiple tags."""
        return await get_tools_by_tags_api(registry, tags, match_all)
    
    @app.tool(
        tags=["registry", "analytics", "usage"],
        description="Record usage of a tool for analytics"
    )
    async def record_tool_usage(tool_name: str) -> Dict[str, str]:
        """Record usage of a tool."""
        return await record_tool_usage_api(registry, tool_name)
    
    logger.info("Registered all registry API tools")