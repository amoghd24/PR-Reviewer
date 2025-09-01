"""Tool metadata API tools."""

from typing import Dict, Any, List, Optional
from global_server.registry import McpServersRegistry
from .utils import format_tool_metadata, format_tool_metadata_simple


async def get_tool_metadata_api(
    registry: McpServersRegistry,
    tool_name: str
) -> Optional[Dict[str, Any]]:
    """Get detailed metadata for a specific tool."""
    metadata = await registry.get_tool_metadata(tool_name)
    if metadata:
        return format_tool_metadata(metadata, include_parameters=True)
    return None


async def get_tools_by_server_api(
    registry: McpServersRegistry,
    server_prefix: str
) -> List[Dict[str, Any]]:
    """Get all tools from a specific server."""
    server_tools = registry.get_tools_by_server(server_prefix)
    return [format_tool_metadata_simple(metadata) for metadata in server_tools]