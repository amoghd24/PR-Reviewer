"""Create task tool implementation."""

import os
from typing import Dict, Any, Optional

from clients.asana import AsanaClient


async def create_task(
    name: str,
    notes: Optional[str] = None,
    assignee: str = "me",
    project_gid: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new Asana task.
    
    Args:
        name: The name/title of the task (required)
        notes: Optional task description/notes
        assignee: Task assignee GID or "me" for current user (default: "me")
        project_gid: Optional project GID to add the task to
        
    Returns:
        Dict containing created task information or error message
        
    Raises:
        ValueError: If required parameters are missing or invalid
        Exception: If API call fails
    """
    if not name or not name.strip():
        raise ValueError("Task name is required and cannot be empty")
    
    # Get environment variables
    token = os.getenv("ASANA_PERSONAL_ACCESS_TOKEN")
    workspace_id = os.getenv("ASANA_WORKSPACE_ID")
    
    if not token:
        raise ValueError("ASANA_PERSONAL_ACCESS_TOKEN environment variable is required")
    if not workspace_id:
        raise ValueError("ASANA_WORKSPACE_ID environment variable is required")
    
    # Initialize client and create task
    client = AsanaClient(token, workspace_id)
    try:
        task = await client.create_task(
            name=name.strip(),
            notes=notes.strip() if notes else None,
            assignee=assignee,
            project_gid=project_gid
        )
        
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