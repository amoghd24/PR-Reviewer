"""Get Pull Request Diff Tool.

Retrieves the unified diff for a pull request showing all code changes.
"""

from typing import Any, Dict
from clients.github import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_pull_request_diff(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get the unified diff for a pull request.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Dictionary containing diff content or error information
    """
    try:
        github_client = GitHubClient()
        
        logger.info(f"Fetching diff for PR #{pull_number} from {owner}/{repo}")
        
        diff_content = await github_client.get_pull_request_diff(owner, repo, pull_number)
        
        result = {
            "status": "success",
            "diff": {
                "owner": owner,
                "repo": repo,
                "pull_number": pull_number,
                "content": diff_content,
                "size_bytes": len(diff_content.encode('utf-8')),
                "lines": len(diff_content.splitlines())
            }
        }
        
        logger.info(f"Successfully retrieved diff for PR #{pull_number} ({result['diff']['lines']} lines)")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get diff for PR #{pull_number} from {owner}/{repo}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "diff": None
        }