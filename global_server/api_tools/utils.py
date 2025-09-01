"""Shared utilities for registry API tools."""

from typing import Dict, Any
from global_server.registry import ToolMetadata


def format_tool_metadata(metadata: ToolMetadata, include_parameters: bool = False) -> Dict[str, Any]:
    """Format tool metadata for API responses."""
    result = {
        "name": metadata.name,
        "description": metadata.description,
        "tags": list(metadata.tags),
        "server_prefix": metadata.server_prefix,
        "usage_count": metadata.usage_count,
        "last_used": metadata.last_used.isoformat() if metadata.last_used else None,
        "is_deprecated": metadata.is_deprecated
    }
    
    if include_parameters:
        result["parameters"] = metadata.parameters
    
    return result


def format_tool_metadata_simple(metadata: ToolMetadata) -> Dict[str, Any]:
    """Format tool metadata for simple API responses."""
    return {
        "name": metadata.name,
        "description": metadata.description,
        "tags": list(metadata.tags),
        "usage_count": metadata.usage_count
    }