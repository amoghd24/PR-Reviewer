"""Get Pull Request Reviews Tool.

Retrieves formal reviews (approved, requested changes, comments) for a pull request.
"""

from typing import Any, Dict
from clients.github import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_pull_request_reviews(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get formal reviews for a pull request.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Dictionary containing reviews information or error information
    """
    try:
        github_client = GitHubClient()
        
        logger.info(f"Fetching reviews for PR #{pull_number} from {owner}/{repo}")
        
        reviews_data = await github_client.get_pull_request_reviews(owner, repo, pull_number)
        
        # Process reviews for easier consumption
        processed_reviews = []
        review_summary = {
            "approved": 0,
            "changes_requested": 0,
            "commented": 0,
            "dismissed": 0
        }
        
        for review in reviews_data:
            state = review.get("state", "").lower()
            processed_review = {
                "id": review["id"],
                "user": review["user"]["login"],
                "state": state,  # APPROVED, REQUEST_CHANGES, COMMENTED, DISMISSED
                "body": review.get("body", ""),
                "submitted_at": review.get("submitted_at"),
                "commit_id": review["commit_id"],
                "html_url": review["html_url"]
            }
            processed_reviews.append(processed_review)
            
            # Update summary counts
            if state == "approved":
                review_summary["approved"] += 1
            elif state == "changes_requested":
                review_summary["changes_requested"] += 1
            elif state == "commented":
                review_summary["commented"] += 1
            elif state == "dismissed":
                review_summary["dismissed"] += 1
        
        result = {
            "status": "success",
            "reviews": {
                "owner": owner,
                "repo": repo,
                "pull_number": pull_number,
                "total_reviews": len(processed_reviews),
                "summary": review_summary,
                "reviews": processed_reviews
            }
        }
        
        logger.info(f"Successfully retrieved {len(processed_reviews)} reviews for PR #{pull_number}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get reviews for PR #{pull_number} from {owner}/{repo}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "reviews": None
        }