"""Get Pull Request Status Tool.

Retrieves status checks and CI/CD information for a pull request.
"""

from typing import Any, Dict
from clients.github import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_pull_request_status(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get status checks for a pull request.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Dictionary containing status information or error information
    """
    try:
        github_client = GitHubClient()
        
        logger.info(f"Fetching status for PR #{pull_number} from {owner}/{repo}")
        
        status_data = await github_client.get_pull_request_status(owner, repo, pull_number)
        
        # Process status data for easier consumption
        processed_statuses = []
        status_summary = {
            "success": 0,
            "pending": 0,
            "failure": 0,
            "error": 0
        }
        
        for status in status_data.get("statuses", []):
            state = status.get("state", "").lower()
            processed_status = {
                "id": status.get("id"),
                "state": state,  # success, pending, failure, error
                "description": status.get("description", ""),
                "target_url": status.get("target_url", ""),
                "context": status.get("context", ""),
                "created_at": status.get("created_at"),
                "updated_at": status.get("updated_at")
            }
            processed_statuses.append(processed_status)
            
            # Update summary counts
            if state in status_summary:
                status_summary[state] += 1
        
        # Overall status from GitHub
        overall_state = status_data.get("state", "pending")
        
        result = {
            "status": "success",
            "pr_status": {
                "owner": owner,
                "repo": repo,
                "pull_number": pull_number,
                "overall_state": overall_state,
                "total_statuses": len(processed_statuses),
                "summary": status_summary,
                "statuses": processed_statuses,
                "sha": status_data.get("sha", ""),
                "total_count": status_data.get("total_count", 0),
                "repository_url": status_data.get("repository", {}).get("html_url", "")
            }
        }
        
        logger.info(f"Successfully retrieved {len(processed_statuses)} statuses for PR #{pull_number} (overall: {overall_state})")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get status for PR #{pull_number} from {owner}/{repo}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "pr_status": None
        }