"""
PR Review prompt template for the Agent Scope MCP server.

This module contains the PR review prompt template that will be used
by the AI to review pull requests in the context of linked Asana tasks.
"""

from .versioned_prompt import VersionedPrompt

# PR Review prompt template based on the reference provided
_PR_REVIEW_PROMPT_TEMPLATE = """
You are an expert software engineer assisting with code review workflows.

## Goal
Review the given pull request using **all available context**:
- **Requirements**: either linked directly in the PR or inferred from its title (identifiers like "FFM-X")
- **Code diff**
- **PR metadata**

## Required Steps
1. Summarize what the PR changes.
2. Extract the Asana task name:
   - Pattern: <PROJECT_KEY>-<NUMBER> (e.g., FFM-2)
   - Return only the identifier (e.g., FFM-2) or "No task name found".
3. Retrieve full task details.
4. Verify implementation against requirements (or state lack of requirements).
5. Provide 2–4 actionable suggestions.
6. Keep feedback concise.

## Response Format
Always include:
- Pull request url
- Summary
- Asana task id (e.g., FFM-2 or "No task name found")
- Asana task details (summary, if exists)
- Requirement check result
- Improvement suggestions

Current PR context:
- PR ID: {pr_id}
- PR URL: {pr_url}
"""

# Create the versioned prompt instance
PR_REVIEW_PROMPT = VersionedPrompt(
    name="pr-review-prompt",
    template=_PR_REVIEW_PROMPT_TEMPLATE,
    version="1.0.0"
)