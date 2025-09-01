"""Find task tool implementation."""

import os
from typing import Dict, Any

from clients.asana import AsanaClient


async def find_task(task_gid: str) -> Dict[str, Any]:
    """Find an Asana task by its GID.
    
    Args:
        task_gid: The global identifier of the task to find
        
    Returns:
        Dict containing task information or error message
        
    Raises:
        ValueError: If task_gid is empty or invalid
        Exception: If API call fails
    """
    if not task_gid or not task_gid.strip():
        raise ValueError("Task GID is required and cannot be empty")
    
    # Get environment variables
    token = os.getenv("ASANA_PERSONAL_ACCESS_TOKEN")
    workspace_id = os.getenv("ASANA_WORKSPACE_ID")
    
    if not token:
        raise ValueError("ASANA_PERSONAL_ACCESS_TOKEN environment variable is required")
    if not workspace_id:
        raise ValueError("ASANA_WORKSPACE_ID environment variable is required")
    
    # Initialize client and find task
    client = AsanaClient(token, workspace_id)
    try:
        task = await client.find_task(task_gid.strip())
        if task is None:
            return {
                "success": False,
                "error": f"Task with GID '{task_gid}' not found",
                "task": None
            }
        
        return {
            "success": True,
            "task": {
                "gid": task.gid,
                "name": task.name,
                "notes": task.notes,
                "completed": task.completed,
                "assignee": task.assignee,
                "workspace": task.workspace,
                "projects": task.projects,
                "created_at": task.created_at,
                "modified_at": task.modified_at
            }
        }
    finally:
        await client.close()