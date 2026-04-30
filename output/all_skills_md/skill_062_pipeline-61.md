```yaml
---
name: issue-workflow-pipeline
description: A multi-stage automated pipeline for processing GitHub issue workflows, including issue inspection, PR correlation, issue management, and CI/CD monitoring.
version: 1.0.0
---

# Issue Workflow Pipeline

## Description

The `issue-workflow-pipeline` is an automated data processing pipeline designed to orchestrate a sequence of GitHub operations related to issue tracking and development workflows. It simulates a common developer task flow: inspecting an issue, finding related merged pull requests, managing the issue state, exporting issue data, adding comments, and monitoring CI/CD runs. The pipeline executes seven stages sequentially, with data automatically passed between stages. Upon completion, the pipeline can be configured to restart for continuous iteration.

## Usage

To use this pipeline, ensure you have the GitHub CLI (`gh`) installed and authenticated. The pipeline requires a target repository and an issue number as primary inputs.

**Basic Invocation:**
```bash
# The pipeline is triggered by specifying the target repository and issue.
# Internal stages are executed automatically.
pipeline-run --repo owner/repo --issue-number 53
```

**Configuration:**
The pipeline can be configured via environment variables or a configuration file to set default repositories, authentication tokens, and output directories.

## Examples

**Example 1: Process a specific issue**
```bash
# This command initiates the pipeline for issue #53 in the octocat/Hello-World repository.
pipeline-run --repo octocat/Hello-World --issue-number 53
```
*Output:*
```
[Stage 1] Viewing issue #53...
[Stage 2] Searching for merged PRs related to the issue's commit SHA...
[Stage 3] Closing issue #53...
[Stage 4] Exporting all issues to issues.json...
[Stage 5] Adding comment to issue #53...
[Stage 6] Watching for CI/CD run completion...
[Stage 7] Verifying final issue state...
Pipeline cycle complete. Ready for next iteration.
```

**Example 2: Using with an environment variable**
```bash
export PIPELINE_DEFAULT_REPO="myorg/myrepo"
pipeline-run --issue-number 101
```

## Pipeline Stages

The pipeline consists of seven distinct stages that execute in a fixed order. Each stage's output may influence subsequent stages.

### Stage 1: Issue Inspection
*   **Description:** Fetches detailed information about a specific GitHub issue using `gh issue view`.
*   **Command:** `gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **Primary Input:** Target repository (`--repo`) and issue number.
*   **Output:** A string containing the issue's title, body, state, labels, and assignees. This data is passed to the next stage.
*   **Next Stage:** Stage 2 (github-cli).

### Stage 2: PR Correlation Search
*   **Description:** Searches for pull requests that have been merged and are associated with the commit SHA referenced in the issue from Stage 1. Uses `gh pr list` with a search filter.
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Input:** Inherits repository context and extracts potential commit SHA from the previous stage's issue data.
*   **Output:** JSON data listing relevant PRs. This confirms if code changes for the issue have been merged.
*   **Next Stage:** Stage 3 (GitHub Development Standard).

### Stage 3: Issue Closure
*   **Description:** Closes the GitHub issue inspected in Stage 1, assuming the related PRs found in Stage 2 indicate resolution.
*   **Command:** `gh issue close <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **Input:** Target repository and issue number from pipeline context.
*   **Output:** Confirmation message indicating the issue was closed.
*   **Next Stage:** Stage 4 (github-cli).

### Stage 4: Issue Data Export
*   **Description:** Exports a comprehensive list of all issues from the repository (open and closed) to a JSON file for record-keeping or analysis.
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Input:** Target repository context.
*   **Output:** A file named `issues.json` containing structured issue data.
*   **Next Stage:** Stage 5 (GitHub Development Standard).

### Stage 5: Issue Commentary
*   **Description:** Adds a standard comment to the now-closed issue to document the resolution context, typically referencing the merged PR.
*   **Command:** `gh issue comment <ISSUE_NUMBER> --repo <OWNER/REPO> --body "Fix implemented via linked PR. Closing issue."`
*   **Input:** Target repository, issue number, and a predefined comment body.
*   **Output:** Confirmation of the comment being posted.
*   **Next Stage:** Stage 6 (github-cli).

### Stage 6: CI/CD Monitoring
*   **Description:** Monitors the latest GitHub Actions workflow run (`gh run watch`) and triggers a system notification upon completion. This simulates waiting for CI checks after a merge.
*   **Command:** `gh run watch && notify-send "CI done!"`
*   **Input:** Repository context to identify the latest run.
*   **Output:** System notification and CLI output indicating the run's final status (success/failure).
*   **Next Stage:** Stage 7 (GitHub Development Standard).

### Stage 7: Final Verification
*   **Description:** Performs a final check on the issue to verify its closed state and the presence of the added comment, ensuring the workflow was executed correctly.
*   **Command:** `gh issue view <ISSUE_NUMBER> --repo <OWNER/REPO>`
*   **Input:** Target repository and issue number.
*   **Output:** A string showing the final state of the issue, confirming closure and updated timeline.
*   **Next Stage:** Pipeline resets to Stage 1 for the next iteration cycle.

---
*Note: This tool is designed for automating development workflow simulations and research.*
```