"""List tasks tool implementation."""

import os
from typing import Dict, Any, Optional

from clients.asana import AsanaClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def list_tasks(
    project_gid: Optional[str] = None,
    assignee: Optional[str] = None,
    completed_since: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """List Asana tasks with optional filters.
    
    Args:
        project_gid: Optional project GID to filter tasks by
        assignee: Optional assignee GID or "me" to filter tasks by
        completed_since: Optional ISO date string for completed tasks filter
        limit: Maximum number of tasks to return (default: 50, max: 100)
        
    Returns:
        Dict containing list of tasks or error message
        
    Raises:
        ValueError: If parameters are invalid
        Exception: If API call fails
    """
    # Validate limit
    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")
    
    # Get environment variables
    token = os.getenv("ASANA_PERSONAL_ACCESS_TOKEN")
    workspace_id = os.getenv("ASANA_WORKSPACE_ID")
    
    if not token:
        raise ValueError("ASANA_PERSONAL_ACCESS_TOKEN environment variable is required")
    if not workspace_id:
        raise ValueError("ASANA_WORKSPACE_ID environment variable is required")
    
    # Initialize client and list tasks
    client = AsanaClient(token, workspace_id)
    try:
        # Build request parameters - O(1) complexity
        params = {
            "opt_fields": "gid,name,notes,completed,assignee,workspace,projects,created_at,modified_at",
            "limit": limit
        }
        
        # Add filters if provided
        if assignee:
            params["assignee"] = assignee
        if completed_since:
            params["completed_since"] = completed_since
        
        # Choose endpoint based on project filter - O(1) decision
        if project_gid:
            endpoint = f"/projects/{project_gid}/tasks"
        else:
            # For workspace tasks, we need assignee filter (use "me" as default)
            endpoint = f"/workspaces/{workspace_id}/tasks"
            if not assignee:
                params["assignee"] = "me"  # Default to current user's tasks
        
        # Single API call - O(1) complexity
        response = await client.client.get(endpoint, params=params)
        response.raise_for_status()
        
        tasks_data = response.json()["data"]
        logger.info(f"Retrieved {len(tasks_data)} tasks")
        
        # Transform to consistent format - O(n) where n = number of tasks returned
        tasks = []
        for task_data in tasks_data:
            tasks.append({
                "gid": task_data.get("gid"),
                "name": task_data.get("name"),
                "notes": task_data.get("notes", ""),
                "completed": task_data.get("completed", False),
                "assignee": task_data.get("assignee"),
                "workspace": task_data.get("workspace"),
                "projects": task_data.get("projects", []),
                "created_at": task_data.get("created_at"),
                "modified_at": task_data.get("modified_at")
            })
        
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
            "filters_applied": {
                "project_gid": project_gid,
                "assignee": assignee,
                "completed_since": completed_since,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            logger.error(f"Response: {e.response.text}")
        return {
            "success": False,
            "error": str(e),
            "tasks": [],
            "count": 0
        }
    finally:
        await client.close()