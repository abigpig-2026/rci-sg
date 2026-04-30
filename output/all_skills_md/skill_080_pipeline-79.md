```yaml
---
name: repo-health-pipeline
description: A multi-stage automated pipeline for continuous repository health monitoring and data collection using GitHub CLI and API.
version: 1.0.0
---

# Repo Health Pipeline

An automated, multi-stage data processing pipeline designed for continuous monitoring and analysis of GitHub repository health metrics. The pipeline executes a sequence of operations to authenticate, collect issue and pull request data, and perform status checks, automatically flowing from one stage to the next. Upon completion, the pipeline resets for the next iteration of monitoring.

## Usage

The pipeline runs autonomously once initiated. It requires a valid GitHub Personal Access Token (PAT) with appropriate repository permissions (e.g., `repo` scope) to be set in the environment.

**Prerequisites:**
1.  Install the GitHub CLI (`gh`).
2.  Authenticate via `gh auth login` or set the `GH_TOKEN` environment variable.

**Basic Execution:**
The pipeline is triggered by its initial stage (authentication). Configure the target repository by setting the `GITHUB_REPOSITORY` environment variable (format: `owner/repo`).

```bash
export GITHUB_REPOSITORY="octocat/Hello-World"
# The pipeline will start automatically upon environment configuration.
```

## Examples

### Example 1: Monitor a Specific Repository
Set the target repository and let the pipeline run its full cycle.

```bash
export GITHUB_REPOSITORY="github/docs"
# Pipeline stages execute sequentially:
# 1. Auth -> 2. List Issues -> 3. Search PRs -> 4. Get PR Details -> 5. Export Issues -> 6. Check PR Status -> 7. Re-auth (Cycle Restart)
```

### Example 2: Integration in a Script
The pipeline's output at each stage can be captured for further processing.

```bash
#!/bin/bash
export GITHUB_REPOSITORY="myorg/myrepo"

# Simulate pipeline stage 2 output (Issue list)
echo "Running Stage 2: Issue Listing"
# Output format: "123: Issue Title"
```

## Pipeline Stages

The pipeline consists of seven sequential stages. Data and state flow automatically from one stage to the next.

### Stage 1: Authentication & Session Initiation
*   **Tool:** `github-cli`
*   **Action:** `gh auth login`
*   **Description:** Initializes the pipeline by establishing an authenticated session with the GitHub API. This stage validates credentials and sets the security context for all subsequent data-fetching operations.
*   **Primary Inputs:** Authentication flags (e.g., `--with-token`, `--hostname`).
*   **Outputs:** Session token, configuration files.
*   **Next Stage:** Flows to **Stage 2**.

### Stage 2: Repository Issue Snapshot
*   **Tool:** `github`
*   **Action:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description:** Fetches a concise list of recent issues from the target repository. Uses `jq` to format the output for readability, providing a quick overview of active work items.
*   **Primary Inputs:** Target repository (`--repo`), output format flags (`--json`, `--jq`).
*   **Outputs:** Formatted string list of issue numbers and titles.
*   **Next Stage:** Flows to **Stage 3**.

### Stage 3: Merged Pull Request Discovery
*   **Tool:** `github-cli`
*   **Action:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Searches for pull requests that have been merged, typically filtered by a commit SHA. This identifies work that has been completed and integrated into the codebase.
*   **Primary Inputs:** Search query (`--search`), state filter (`--state`), output flags.
*   **Outputs:** JSON data containing merged PR numbers, titles, and URLs.
*   **Next Stage:** Flows to **Stage 4**.

### Stage 4: Detailed Pull Request Inspection
*   **Tool:** `github`
*   **Action:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Description:** Makes a direct API call to retrieve detailed metadata for a specific pull request (e.g., PR #55). Extracts key fields like title, current state, and author.
*   **Primary Inputs:** API endpoint path, `jq` filter.
*   **Outputs:** Formatted string with PR details.
*   **Next Stage:** Flows to **Stage 5**.

### Stage 5: Comprehensive Issue Data Export
*   **Tool:** `github-cli`
*   **Action:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Performs a bulk export of nearly all issues from the repository, capturing their state, labels, and assignees. This creates a persistent dataset (`issues.json`) for historical analysis or reporting.
*   **Primary Inputs:** State filter (`--state all`), high limit, extensive JSON field selection.
*   **Outputs:** A JSON file (`issues.json`) containing rich issue data.
*   **Next Stage:** Flows to **Stage 6**.

### Stage 6: Pull Request Status Verification
*   **Tool:** `github`
*   **Action:** `gh pr checks 55 --repo owner/repo`
*   **Description:** Checks the status of continuous integration (CI) checks for a specific pull request. This validates whether the PR meets all required quality gates before merging.
*   **Primary Inputs:** PR number, target repository.
*   **Outputs:** Status report of CI checks (e.g., pending, passed, failed).
*   **Next Stage:** Flows to **Stage 7**.

### Stage 7: Session Renewal & Cycle Restart
*   **Tool:** `github-cli`
*   **Action:** `gh auth login`
*   **Description:** Re-authenticates or refreshes the session. This stage completes the loop and resets the pipeline, preparing it for the next monitoring iteration to ensure long-running operation.
*   **Primary Inputs:** Authentication flags.
*   **Outputs:** Renewed session credentials.
*   **Next Stage:** Flows back to **Stage 1** to begin the next cycle.
```