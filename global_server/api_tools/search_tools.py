"""Tool search and discovery API tools."""

from typing import Dict, Any, List, Optional
from global_server.registry import McpServersRegistry
from .utils import format_tool_metadata


async def search_tools_api(
    registry: McpServersRegistry,
    query: Optional[str] = None,
    tags: Optional[List[str]] = None,
    server_prefix: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Search for tools with multiple filters."""
    results = await registry.search_tools(query, tags, server_prefix, limit)
    return [format_tool_metadata(metadata) for metadata in results]


async def get_tools_by_tags_api(
    registry: McpServersRegistry,
    tags: List[str], 
    match_all: bool = True
) -> List[str]:
    """Get tools matching multiple tags."""
    matching_tools = await registry.get_tools_by_tags(tags, match_all)
    return list(matching_tools.keys())