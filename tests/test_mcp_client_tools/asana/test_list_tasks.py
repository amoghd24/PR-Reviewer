"""Test Asana list_tasks tool."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_asana_list_tasks():
    """Test listing Asana tasks."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "asana_list_tasks_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure
        import json
        data = json.loads(result[0].text)
        assert data["success"] == True
        assert "tasks" in data
        assert isinstance(data["tasks"], list)


def test_asana_list_tasks_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_asana_list_tasks())