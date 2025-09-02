"""Test Registry search tools."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_registry_search_tools():
    """Test searching tools by query."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "search_tools", {
            "query": "asana"
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure - returns array directly
        import json
        data = json.loads(result[0].text)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]


def test_registry_search_tools_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_registry_search_tools())