"""Test Registry get_tool_metadata."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_registry_get_tool_metadata():
    """Test getting tool metadata."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "get_tool_metadata", {
            "tool_name": "asana_list_tasks_tool"
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure - returns object directly
        import json
        data = json.loads(result[0].text)
        assert isinstance(data, dict)
        assert data["name"] == "asana_list_tasks_tool"
        assert "description" in data


def test_registry_get_tool_metadata_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_registry_get_tool_metadata())