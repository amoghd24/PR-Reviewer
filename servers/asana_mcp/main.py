"""Asana MCP Server - PR-1 Implementation.

A FastMCP server providing Asana task management tools for the PR reviewer system.
Implements find_task() and create_task() tools with proper error handling and validation.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from utils.logger import get_logger
from .tools.find_task import find_task
from .tools.create_task import create_task
from .tools.list_tasks import list_tasks

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger(__name__)

# Initialize FastMCP server
app = FastMCP(
    name="asana-mcp-server",
    version="0.1.0"
)


@app.tool(
    tags=["asana", "task", "search", "pr-reviewer"],
    description="Find an Asana task by its Global ID (GID)"
)
async def find_task_tool(task_gid: str) -> dict:
    """Find an Asana task by its GID."""
    return await find_task(task_gid)


@app.tool(
    tags=["asana", "task", "create", "pr-reviewer"],
    description="Create a new Asana task with optional assignee and project"
)
async def create_task_tool(
    name: str,
    notes: Optional[str] = None,
    assignee: str = "me",
    project_gid: Optional[str] = None
) -> dict:
    """Create a new Asana task."""
    return await create_task(name, notes, assignee, project_gid)


@app.tool(
    tags=["asana", "task", "list", "pr-reviewer"],
    description="List Asana tasks with optional filters for project, assignee, and completion status"
)
async def list_tasks_tool(
    project_gid: Optional[str] = None,
    assignee: Optional[str] = None,
    completed_since: Optional[str] = None,
    limit: int = 50
) -> dict:
    """List Asana tasks with optional filters."""
    return await list_tasks(project_gid, assignee, completed_since, limit)




if __name__ == "__main__":
    # Validate environment variables on startup
    required_vars = ["ASANA_PERSONAL_ACCESS_TOKEN", "ASANA_WORKSPACE_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set the required environment variables and restart the server")
        exit(1)
    
    logger.info("Starting Asana MCP Server")
    logger.info(f"Workspace ID: {os.getenv('ASANA_WORKSPACE_ID')}")
    
    # Run the FastMCP server
    app.run()