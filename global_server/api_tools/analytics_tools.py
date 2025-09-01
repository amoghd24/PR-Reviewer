"""Tool analytics and statistics API tools."""

from typing import Dict, Any, List
from global_server.registry import McpServersRegistry
from .utils import format_tool_metadata


async def get_tag_statistics_api(registry: McpServersRegistry) -> Dict[str, int]:
    """Get usage statistics for all tags."""
    return registry.get_tag_statistics()


async def get_popular_tools_api(
    registry: McpServersRegistry,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get most frequently used tools."""
    popular_tools = registry.get_popular_tools(limit)
    return [format_tool_metadata(metadata) for metadata in popular_tools]


async def record_tool_usage_api(
    registry: McpServersRegistry,
    tool_name: str
) -> Dict[str, str]:
    """Record usage of a tool."""
    registry.record_tool_usage(tool_name)
    return {"status": "recorded", "tool": tool_name}