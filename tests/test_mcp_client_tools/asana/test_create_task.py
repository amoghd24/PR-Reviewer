"""Test Asana create_task tool."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_asana_create_task():
    """Test creating an Asana task."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        result = await client.call_tool("global", "asana_create_task_tool", {
            "name": "Test task from MCP Client",
            "notes": "Created via integration test"
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Check JSON structure
        import json
        data = json.loads(result[0].text)
        assert data["success"] == True
        assert "task" in data
        assert data["task"]["name"] == "Test task from MCP Client"


def test_asana_create_task_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_asana_create_task())