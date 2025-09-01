"""List Pull Requests Tool.

Retrieves all pull requests for a repository with their metadata including PR numbers and descriptions.
"""

from typing import Any, Dict, Optional
from clients.github import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def list_pull_requests(
    owner: str, 
    repo: str, 
    state: str = "all", 
    limit: int = 30,
    sort: str = "updated"
) -> Dict[str, Any]:
    """
    List pull requests for a repository with their metadata.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        state: State of PRs to retrieve (open, closed, all). Default: "all"
        limit: Maximum number of PRs to return. Default: 30
        sort: Sort order (created, updated, popularity, long-running). Default: "updated"
        
    Returns:
        Dictionary containing PRs list or error information
    """
    try:
        github_client = GitHubClient()
        
        logger.info(f"Fetching pull requests from {owner}/{repo} (state: {state}, limit: {limit})")
        
        # GitHub API endpoint for listing PRs
        import httpx
        async with httpx.AsyncClient() as client:
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            headers = {
                "Authorization": f"Bearer {github_client.access_token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "pr-reviewer-mcp/0.1.0"
            }
            params = {
                "state": state,
                "sort": sort,
                "direction": "desc",
                "per_page": min(limit, 100)  # GitHub API max is 100
            }
            
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            prs_data = response.json()
        
        # Process PR data for easier consumption
        processed_prs = []
        
        for pr in prs_data:
            pr_body = pr.get("body") or ""  # Handle None case
            processed_pr = {
                "number": pr["number"],
                "title": pr["title"],
                "description": pr_body[:500] + ("..." if len(pr_body) > 500 else ""),  # Truncate long descriptions
                "state": pr["state"],
                "author": pr["user"]["login"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "base_branch": pr["base"]["ref"],
                "head_branch": pr["head"]["ref"],
                "draft": pr.get("draft", False),
                "merged": pr.get("merged", False),
                "mergeable": pr.get("mergeable"),
                "url": pr["html_url"],
                "additions": pr.get("additions", 0),
                "deletions": pr.get("deletions", 0),
                "changed_files": pr.get("changed_files", 0),
                "commits": pr.get("commits", 0),
                "comments": pr.get("comments", 0),
                "review_comments": pr.get("review_comments", 0),
                "labels": [label["name"] for label in pr.get("labels", [])],
                "assignees": [assignee["login"] for assignee in pr.get("assignees", [])],
                "reviewers": [reviewer["login"] for reviewer in pr.get("requested_reviewers", [])],
            }
            processed_prs.append(processed_pr)
        
        # Summary statistics
        summary = {
            "total_found": len(processed_prs),
            "open_count": len([pr for pr in processed_prs if pr["state"] == "open"]),
            "closed_count": len([pr for pr in processed_prs if pr["state"] == "closed"]),
            "draft_count": len([pr for pr in processed_prs if pr["draft"]]),
            "merged_count": len([pr for pr in processed_prs if pr["merged"]]),
        }
        
        result = {
            "status": "success",
            "repository": {
                "owner": owner,
                "repo": repo,
                "query_params": {
                    "state": state,
                    "limit": limit,
                    "sort": sort
                },
                "summary": summary,
                "pull_requests": processed_prs
            }
        }
        
        logger.info(f"Successfully retrieved {len(processed_prs)} pull requests from {owner}/{repo}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to list pull requests from {owner}/{repo}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "repository": None
        }