```yaml
---
name: issue-workflow-automation
description: A multi-stage automated pipeline for processing GitHub issue workflows, including viewing, closing, commenting, and gathering related data.
version: 1.0.0
---

# Issue Workflow Automation

This skill implements an automated, multi-stage data processing pipeline for managing GitHub issue workflows. The pipeline sequentially executes a series of GitHub CLI (`gh`) commands to perform a complete issue lifecycle operation and gather contextual data. Each stage's output can inform subsequent stages, and upon completion, the pipeline is designed to restart for the next iteration.

## Usage

To use this pipeline, you must have the GitHub CLI (`gh`) installed and authenticated. The pipeline requires a target repository specified in the format `owner/repo` and an issue number to operate on.

**Basic Invocation:**
The pipeline is triggered by providing the target repository and an initial issue number. The pipeline will automatically progress through all defined stages.

**Prerequisites:**
- GitHub CLI (`gh`) installed.
- Valid `gh` authentication (`gh auth login`).
- Appropriate permissions on the target repository.

## Examples

**Example 1: Process a specific issue**
This command initiates the pipeline for issue `53` in the `octocat/Hello-World` repository.
```bash
# The pipeline would be configured to start with these parameters
REPO="octocat/Hello-World"
ISSUE_NUMBER=53
```

**Example 2: Expected Pipeline Output Flow**
1.  Stage 1 retrieves details for issue #53.
2.  Stage 2 searches for merged PRs related to the commit SHA found in the issue.
3.  Stage 3 closes issue #53.
4.  Stage 4 exports a complete list of all repository issues to `issues.json`.
5.  Stage 5 adds a comment "修复说明..." to issue #53.
6.  Stage 6 fetches and formats contributor statistics.
7.  Stage 7 verifies the final state of issue #53.

## Pipeline Stages

The pipeline consists of seven sequential stages that execute and pass data automatically.

### Stage 1: View Target Issue
*   **Command:** `gh issue view <ISSUE_NUMBER> --repo <REPO>`
*   **Description:** Fetches and displays the full details (title, body, state, labels, etc.) of the specified issue. This establishes the initial context for the workflow.
*   **Input:** Repository (`owner/repo`), Issue Number.
*   **Output:** A string containing the formatted issue details.
*   **Next Stage:** Flows to `github-cli` (Stage 2).

### Stage 2: Search for Related Merged Pull Requests
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Searches for pull requests that have been merged and are associated with a specific commit SHA (typically extracted from the issue body or comments in Stage 1). Outputs key PR data in JSON format.
*   **Input:** Accepts numerous `gh` global and command-specific flags. The critical input for this stage is the `--search` query, which should be populated with the relevant SHA.
*   **Output:** JSON array containing PR numbers, titles, and URLs. May also output debug files or raw HTTP traces.
*   **Next Stage:** Flows to `GitHub Development Standard` (Stage 3).

### Stage 3: Close the Target Issue
*   **Command:** `gh issue close <ISSUE_NUMBER> --repo <REPO>`
*   **Description:** Closes the specified issue. This action is typically performed after verifying a related fix has been merged (as suggested by Stage 2).
*   **Input:** Repository (`owner/repo`), Issue Number.
*   **Output:** A confirmation string indicating the issue was closed.
*   **Next Stage:** Flows to `github-cli` (Stage 4).

### Stage 4: Export Repository Issues Snapshot
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Exports a comprehensive snapshot of all issues in the repository (open and closed) to a local JSON file named `issues.json`. This provides a audit point and dataset for analysis.
*   **Input:** Utilizes `gh issue list` flags to get all states, a high limit, and specific JSON fields.
*   **Output:** A file named `issues.json` containing the issue data.
*   **Next Stage:** Flows to `GitHub Development Standard` (Stage 5).

### Stage 5: Add Resolution Comment to Issue
*   **Command:** `gh issue comment <ISSUE_NUMBER> --repo <REPO> --body "修复说明..."`
*   **Description:** Adds a follow-up comment to the now-closed issue. The comment body should explain the resolution, often referencing the merged PR from Stage 2.
*   **Input:** Repository (`owner/repo`), Issue Number, Comment Body.
*   **Output:** A confirmation string indicating the comment was posted.
*   **Next Stage:** Flows to `github-cli` (Stage 6).

### Stage 6: Fetch Contributor Statistics
*   **Command:** `gh api --paginate repos/<REPO>/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -`
*   **Description:** Calls the GitHub API to fetch contributor data for the repository, formats it using `jq` to show `login: contributions`, and pipes to `head`. This provides contextual information about the project's contributors.
*   **Input:** Repository path for the API endpoint, pagination flag, and a `jq` filter.
*   **Output:** Formatted lines showing contributor usernames and their contribution counts.
*   **Next Stage:** Flows to `GitHub Development Standard` (Stage 7).

### Stage 7: Verify Final Issue State
*   **Command:** `gh issue view <ISSUE_NUMBER> --repo <REPO>`
*   **Description:** A final verification step. Fetches the issue details again to confirm its state is now `closed` and that the resolution comment from Stage 5 is present.
*   **Input:** Repository (`owner/repo`), Issue Number.
*   **Output:** A string containing the updated issue details, showing the closed state and new comment.
*   **Next Stage:** Flows back to Stage 1, ready for the next iteration with new parameters.

---
*Note: This tool is designed for automating legitimate repository maintenance tasks. Ensure you have authorization to perform these actions on the target repository.*
```