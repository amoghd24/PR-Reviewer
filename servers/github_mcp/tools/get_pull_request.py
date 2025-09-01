"""Get Pull Request Tool.

Retrieves comprehensive pull request information including metadata, author, and status.
"""

from typing import Any, Dict
from clients.github import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_pull_request(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get detailed information about a pull request.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Dictionary containing PR details or error information
    """
    try:
        github_client = GitHubClient()
        
        logger.info(f"Fetching pull request #{pull_number} from {owner}/{repo}")
        
        pr_data = await github_client.get_pull_request(owner, repo, pull_number)
        
        # Extract key information for PR review
        result = {
            "status": "success",
            "pull_request": {
                "number": pr_data["number"],
                "title": pr_data["title"],
                "body": pr_data.get("body", ""),
                "state": pr_data["state"],
                "author": pr_data["user"]["login"],
                "created_at": pr_data["created_at"],
                "updated_at": pr_data["updated_at"],
                "base_branch": pr_data["base"]["ref"],
                "head_branch": pr_data["head"]["ref"],
                "mergeable": pr_data.get("mergeable"),
                "merged": pr_data["merged"],
                "draft": pr_data["draft"],
                "url": pr_data["html_url"],
                "additions": pr_data.get("additions", 0),
                "deletions": pr_data.get("deletions", 0),
                "changed_files": pr_data.get("changed_files", 0),
                "commits": pr_data.get("commits", 0),
                "comments": pr_data.get("comments", 0),
                "review_comments": pr_data.get("review_comments", 0),
                "labels": [label["name"] for label in pr_data.get("labels", [])],
                "assignees": [assignee["login"] for assignee in pr_data.get("assignees", [])],
                "reviewers": [reviewer["login"] for reviewer in pr_data.get("requested_reviewers", [])],
            }
        }
        
        logger.info(f"Successfully retrieved PR #{pull_number}: {pr_data['title']}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get pull request #{pull_number} from {owner}/{repo}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "pull_request": None
        }