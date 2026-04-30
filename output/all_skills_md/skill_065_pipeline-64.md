```yaml
---
name: issue-workflow-pipeline
description: A multi-stage automated pipeline for processing GitHub issue workflows, including viewing, closing, commenting, and extracting related data.
version: 1.0.0
---

# Issue Workflow Pipeline

This skill implements an automated, multi-stage data processing pipeline for managing GitHub issue workflows. The pipeline sequentially executes a series of GitHub CLI (`gh`) commands to perform a complete issue lifecycle operation, including inspection, closure, commenting, and data aggregation. Each stage's output can serve as input or context for subsequent stages, creating a continuous processing loop.

## Usage

To execute the pipeline, you must have the GitHub CLI (`gh`) installed and authenticated. The pipeline requires a target repository and a specific issue number to operate on.

**Basic Invocation:**
```bash
# The pipeline is triggered by specifying the target repository and issue.
# It will automatically progress through all defined stages.
./issue-workflow-pipeline --repo owner/repo --issue-number 53
```

**Required Parameters:**
- `--repo` or `-R`: The target repository in `owner/repo` format.
- `--issue-number` or `-n`: The numeric identifier of the issue to process.

**Optional Parameters:**
- `--comment-body` or `-b`: Custom text for the comment added in stage 5. Defaults to "修复说明...".
- `--search-sha` or `-s`: A commit SHA to search for merged pull requests in stage 2.

## Examples

**Example 1: Process a specific issue**
This command runs the full pipeline for issue #53 in the `octocat/Hello-World` repository.
```bash
./issue-workflow-pipeline --repo octocat/Hello-World --issue-number 53
```

**Example 2: Process an issue with a custom comment and SHA search**
This command processes issue #101, adds a specific comment, and searches for PRs related to commit `a1b2c3d`.
```bash
./issue-workflow-pipeline \
  --repo github/docs \
  --issue-number 101 \
  --comment-body "Automated fix applied via pipeline. See linked PR." \
  --search-sha a1b2c3d
```

**Example 3: Dry run to preview actions**
Some stages support a `--dry-run` flag to preview commands without execution.
```bash
./issue-workflow-pipeline --repo owner/repo --issue-number 7 --dry-run
```

## Pipeline Stages

The pipeline consists of seven sequential stages. Upon completion of stage 7, the pipeline can be configured to loop back to stage 1 for continuous monitoring or batch processing.

### Stage 1: Issue Inspection
*   **Command:** `gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **Description:** Fetches and displays the complete details of the target issue. This establishes the initial context, confirming the issue exists and retrieving its current state (open, closed, labels, assignees).
*   **Input:** Repository identifier and issue number.
*   **Output:** A detailed string representation of the issue (title, body, state, metadata).
*   **Next Stage:** Flows to Stage 2 (github-cli).

### Stage 2: Pull Request Correlation
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Searches for pull requests that have been merged and are associated with a specific commit SHA (potentially extracted or inferred from the issue in a real-world scenario). This stage gathers related development activity.
*   **Input:** A commit SHA (e.g., from issue comments or linked commits).
*   **Output:** JSON array containing the numbers, titles, and URLs of merged PRs. May also output debug files or raw HTTP traces.
*   **Next Stage:** Flows to Stage 3 (GitHub Development Standard).

### Stage 3: Issue Closure
*   **Command:** `gh issue close <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **Description:** Closes the target issue. This typically follows confirmation that related work (e.g., a PR from Stage 2) has been completed.
*   **Input:** Repository identifier and issue number.
*   **Output:** Confirmation message string indicating the issue was closed.
*   **Next Stage:** Flows to Stage 4 (github-cli).

### Stage 4: Repository Issue Snapshot
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Exports a comprehensive snapshot of all issues in the repository (open and closed) to a JSON file. This provides aggregate data for reporting or analysis after the target issue is closed.
*   **Input:** Repository identifier.
*   **Output:** A JSON file (`issues.json`) containing an array of issue objects with key fields.
*   **Next Stage:** Flows to Stage 5 (GitHub Development Standard).

### Stage 5: Issue Commentary
*   **Command:** `gh issue comment <ISSUE_NUMBER> --repo <OWNER/REPO> --body "修复说明..."`
*   **Description:** Adds a final comment to the now-closed issue. The comment typically provides closure context, links to related PRs, or a summary of the fix.
*   **Input:** Repository identifier, issue number, and comment body text.
*   **Output:** Confirmation message string indicating the comment was posted.
*   **Next Stage:** Flows to Stage 6 (github-cli).

### Stage 6: User Context Enrichment
*   **Command:** `gh api --paginate user/starred --jq '.[].full_name' | head -20`
*   **Description:** Calls the GitHub API to list repositories starred by the authenticated user, extracting their full names. This enriches the pipeline context with user preference data, which could inform subsequent automation decisions.
*   **Input:** None (uses authenticated user context).
*   **Output:** A list of up to 20 repository full names (e.g., `owner/repo`).
*   **Next Stage:** Flows to Stage 7 (GitHub Development Standard).

### Stage 7: Final Verification
*   **Command:** `gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **Description:** Performs a final view of the target issue to verify its state post-processing (should be closed with the added comment). This serves as the pipeline's validation step.
*   **Input:** Repository identifier and issue number.
*   **Output:** A detailed string representation of the issue's final state.
*   **Next Stage:** By default, the pipeline terminates. It can be configured to loop back to Stage 1 for processing the next issue in a queue.

---
*Note: This tool is designed for automating legitimate repository maintenance tasks. Use responsibly and in accordance with GitHub's Terms of Service.*
```