"""Get Pull Request Files Tool.

Retrieves the list of files changed in a pull request with their modifications.
"""

from typing import Any, Dict
from clients.github import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_pull_request_files(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """
    Get the list of files changed in a pull request.
    
    Args:
        owner: Repository owner/organization name
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Dictionary containing files information or error information
    """
    try:
        github_client = GitHubClient()
        
        logger.info(f"Fetching files for PR #{pull_number} from {owner}/{repo}")
        
        files_data = await github_client.get_pull_request_files(owner, repo, pull_number)
        
        # Process files data for easier consumption
        processed_files = []
        total_additions = 0
        total_deletions = 0
        
        for file_info in files_data:
            processed_file = {
                "filename": file_info["filename"],
                "status": file_info["status"],  # added, removed, modified, renamed
                "additions": file_info.get("additions", 0),
                "deletions": file_info.get("deletions", 0),
                "changes": file_info.get("changes", 0),
                "patch": file_info.get("patch", ""),
                "blob_url": file_info.get("blob_url", ""),
                "raw_url": file_info.get("raw_url", ""),
            }
            
            # Handle renamed files
            if file_info.get("previous_filename"):
                processed_file["previous_filename"] = file_info["previous_filename"]
                
            processed_files.append(processed_file)
            total_additions += processed_file["additions"]
            total_deletions += processed_file["deletions"]
        
        result = {
            "status": "success",
            "files": {
                "owner": owner,
                "repo": repo,
                "pull_number": pull_number,
                "total_files": len(processed_files),
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "total_changes": total_additions + total_deletions,
                "files": processed_files
            }
        }
        
        logger.info(f"Successfully retrieved {len(processed_files)} files for PR #{pull_number}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to get files for PR #{pull_number} from {owner}/{repo}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "files": None
        }