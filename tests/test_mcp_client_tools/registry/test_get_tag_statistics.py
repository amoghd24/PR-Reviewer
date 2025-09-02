"""Test Registry get_tag_statistics."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_registry_get_tag_statistics():
    """Test getting tag statistics."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "get_tag_statistics", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure - returns object directly  
        import json
        data = json.loads(result[0].text)
        assert isinstance(data, dict)
        # Statistics should have tag counts
        assert len(data) > 0


def test_registry_get_tag_statistics_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_registry_get_tag_statistics())