"""Get Pull Request Comments Tool.

Retrieves review comments and discussion for a pull request.
"""

from typing import Any, Dict
from clients.github import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_pull_request_comments(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get review comments for a pull request.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Dictionary containing comments information or error information
    """
    try:
        github_client = GitHubClient()
        
        logger.info(f"Fetching comments for PR #{pull_number} from {owner}/{repo}")
        
        comments_data = await github_client.get_pull_request_comments(owner, repo, pull_number)
        
        # Process comments for easier consumption
        processed_comments = []
        
        for comment in comments_data:
            processed_comment = {
                "id": comment["id"],
                "user": comment["user"]["login"],
                "body": comment["body"],
                "created_at": comment["created_at"],
                "updated_at": comment["updated_at"],
                "path": comment.get("path", ""),
                "position": comment.get("position"),
                "original_position": comment.get("original_position"),
                "line": comment.get("line"),
                "original_line": comment.get("original_line"),
                "side": comment.get("side", "RIGHT"),  # LEFT or RIGHT
                "start_line": comment.get("start_line"),
                "start_side": comment.get("start_side"),
                "in_reply_to_id": comment.get("in_reply_to_id"),
                "url": comment["html_url"]
            }
            processed_comments.append(processed_comment)
        
        result = {
            "status": "success",
            "comments": {
                "owner": owner,
                "repo": repo,
                "pull_number": pull_number,
                "total_comments": len(processed_comments),
                "comments": processed_comments
            }
        }
        
        logger.info(f"Successfully retrieved {len(processed_comments)} comments for PR #{pull_number}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get comments for PR #{pull_number} from {owner}/{repo}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "comments": None
        }