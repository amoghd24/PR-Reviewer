"""Test Asana find_task tool."""

import asyncio
import pytest
from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_asana_find_task():
    """Test finding an Asana task by GID."""
    async with MCPClient() as client:
        await client.connect("global", "uv", ["run", "python", "-m", "global_server.server"])
        
        # First get a task to find
        tasks_result = await client.call_tool("global", "asana_list_tasks_tool", {})
        import json
        tasks_data = json.loads(tasks_result[0].text)
        
        if tasks_data["tasks"]:
            task_gid = tasks_data["tasks"][0]["gid"]
            
            result = await client.call_tool("global", "asana_find_task_tool", {
                "gid": task_gid
            })
            
            assert len(result) == 1
            assert result[0].type == "text"
            
            data = json.loads(result[0].text)
            assert data["success"] == True
            assert data["task"]["gid"] == task_gid


def test_asana_find_task_sync():
    """Synchronous wrapper for manual testing."""
    asyncio.run(test_asana_find_task())