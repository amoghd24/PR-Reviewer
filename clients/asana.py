"""Asana API client for MCP server integration."""

from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from utils.logger import get_logger

logger = get_logger(__name__)


class AsanaTask(BaseModel):
    """Asana task model with essential fields."""
    
    gid: str
    name: str
    notes: Optional[str] = ""
    completed: bool = False
    assignee: Optional[Dict[str, Any]] = None
    workspace: Dict[str, Any]
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


class AsanaClient:
    """Async HTTP client for Asana API operations."""
    
    BASE_URL = "https://app.asana.com/api/1.0"
    
    def __init__(self, personal_access_token: str, workspace_id: str):
        """Initialize Asana client.
        
        Args:
            personal_access_token: Asana PAT for authentication
            workspace_id: Default workspace GID for operations
        """
        self.workspace_id = workspace_id
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {personal_access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    
    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()
    
    async def find_task(self, task_gid: str) -> Optional[AsanaTask]:
        """Find a task by GID with O(1) complexity.
        
        Args:
            task_gid: Global ID of the task to retrieve
            
        Returns:
            AsanaTask if found, None otherwise
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = await self.client.get(
                f"/tasks/{task_gid}",
                params={
                    "opt_fields": "gid,name,notes,completed,assignee,workspace,projects,created_at,modified_at"
                }
            )
            response.raise_for_status()
            
            task_data = response.json()["data"]
            return AsanaTask(**task_data)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Task {task_gid} not found")
                return None
            logger.error(f"HTTP error finding task {task_gid}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error finding task {task_gid}: {e}")
            raise
    
    async def create_task(
        self,
        name: str,
        notes: Optional[str] = None,
        assignee: str = "me",
        project_gid: Optional[str] = None,
    ) -> AsanaTask:
        """Create a new task with O(1) complexity.
        
        Args:
            name: Task name (required)
            notes: Task description/notes
            assignee: Assignee GID or "me" for current user
            project_gid: Project GID to add task to
            
        Returns:
            Created AsanaTask
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If required parameters are missing
        """
        if not name or not name.strip():
            raise ValueError("Task name is required and cannot be empty")
        
        task_data = {
            "workspace": self.workspace_id,
            "name": name.strip(),
            "assignee": assignee,
        }
        
        if notes:
            task_data["notes"] = notes.strip()
        
        if project_gid:
            task_data["projects"] = [project_gid]
        
        try:
            response = await self.client.post(
                "/tasks",
                json={"data": task_data},
                params={
                    "opt_fields": "gid,name,notes,completed,assignee,workspace,projects,created_at,modified_at"
                }
            )
            response.raise_for_status()
            
            created_task = response.json()["data"]
            logger.info(f"Created task: {created_task['gid']} - {created_task['name']}")
            return AsanaTask(**created_task)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating task: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise