```yaml
---
name: repo-workflow-analyzer
description: A multi-stage automated data processing pipeline for GitHub repository workflow analysis and monitoring.
version: 1.0.0
---

# Repo Workflow Analyzer

The Repo Workflow Analyzer is an automated, multi-stage data processing pipeline designed to collect, analyze, and monitor key metrics and activities within GitHub repositories. It orchestrates a sequence of GitHub CLI and API operations to extract structured data on issues, pull requests, and workflow runs, facilitating continuous repository health assessment.

## Usage

To execute the pipeline, ensure you have the GitHub CLI (`gh`) installed and authenticated. The pipeline runs sequentially, with the output of one stage potentially influencing the input or behavior of the next. After the final stage completes, the pipeline can be configured to restart for continuous monitoring cycles.

**Basic Execution:**
```bash
# The pipeline stages are executed in order. Configuration (like target repo) is typically set at initiation.
./trigger-pipeline.sh --repo owner/repository-name
```

**Key Configuration Parameters:**
*   `--repo`: Specifies the target repository in `owner/name` format.
*   `--run-id`: The ID of a specific workflow run for detailed inspection (Stage 6).
*   `--search-sha`: A commit SHA used to search for related merged pull requests (Stage 3).

## Examples

**Example 1: Full Repository Analysis Cycle**
This example runs a complete analysis on the `octocat/Hello-World` repo, searching for PRs merged from a specific commit (`a1b2c3d`).
```bash
# Configure pipeline target
export PIPELINE_TARGET_REPO="octocat/Hello-World"
export SEARCH_SHA="a1b2c3d"
export WORKFLOW_RUN_ID="1234567890"

# Execute the pipeline sequence
pipeline-executor --start
```
*Expected Output Flow:*
1.  Authentication confirmed.
2.  List of recent issues printed to console.
3.  List of PRs merged containing the specified SHA.
4.  Details of a specific pull request (#55) fetched.
5.  Comprehensive issue list exported to `issues.json`.
6.  Details of a specific workflow run viewed.
7.  Authentication re-validated for the next cycle.

**Example 2: Generating an Issue Snapshot**
To quickly generate a JSON snapshot of all issues (Stage 5 output) without running the full pipeline:
```bash
gh issue list --repo octocat/Hello-World --state all --limit 9999 --json number,title,state,labels,assignees > issue_snapshot_$(date +%Y%m%d).json
```

## Pipeline Stages

The pipeline consists of seven sequential stages. Data flows from one stage to the next automatically upon successful completion.

### Stage 1: Authentication & Session Initiation
*   **Tool:** `github-cli`
*   **Command:** `gh auth login`
*   **Description:** Initializes and verifies the CLI session with GitHub. This stage ensures all subsequent API calls have the necessary permissions. It handles token management and host configuration.
*   **Primary Inputs:** Authentication flags (e.g., `--with-token`, `--hostname`).
*   **Outputs:** Establishes an authenticated session state for the pipeline.
*   **Next Stage:** github

### Stage 2: Issue Listing & Summary
*   **Tool:** `github`
*   **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description:** Fetches a concise, formatted list of recent issues from the target repository. Uses `jq` to parse JSON output into a readable string format for quick review.
*   **Primary Inputs:** Target repository (`--repo`), output format (`--json`), query filter (`--jq`).
*   **Outputs:** A formatted string list of issue numbers and titles printed to the console/result stream.
*   **Next Stage:** github-cli

### Stage 3: Pull Request Search by Commit
*   **Tool:** `github-cli`
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Searches for pull requests that have been merged and contain a specific commit SHA in their history. Useful for tracing changes and understanding integration points.
*   **Primary Inputs:** Search query (`--search`), state filter (`--state`), output schema (`--json`).
*   **Outputs:** JSON array containing the number, title, and URL of matching PRs.
*   **Next Stage:** github

### Stage 4: Detailed Pull Request Inspection
*   **Tool:** `github`
*   **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Description:** Makes a direct API call to fetch granular details for a specific pull request (e.g., #55). Extracts key fields like title, current state, and author.
*   **Primary Inputs:** API endpoint path, query filter (`--jq`).
*   **Outputs:** A string containing the title, state, and author's login of the specified PR.
*   **Next Stage:** github-cli

### Stage 5: Comprehensive Issue Data Export
*   **Tool:** `github-cli`
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Performs a bulk export of all issues (open and closed) with extensive metadata, including labels and assignees. Output is redirected to a JSON file for persistent storage or further analysis.
*   **Primary Inputs:** State filter (`--state all`), high limit (`--limit`), comprehensive output schema (`--json`).
*   **Outputs:** A file named `issues.json` containing a complete dataset of repository issues.
*   **Next Stage:** github

### Stage 6: Workflow Run Analysis
*   **Tool:** `github`
*   **Command:** `gh run view <run-id> --repo owner/repo`
*   **Description:** Retrieves the status, logs, and conclusion details of a specific GitHub Actions workflow run. This is critical for CI/CD pipeline monitoring and debugging.
*   **Primary Inputs:** Workflow run identifier (`<run-id>`), target repository (`--repo`).
*   **Outputs:** Detailed summary of the workflow run, including status, jobs, and duration, printed to the console.
*   **Next Stage:** github-cli

### Stage 7: Session Re-validation
*   **Tool:** `github-cli`
*   **Command:** `gh auth login`
*   **Description:** Re-executes authentication to refresh the session token and ensure continued validity for the next pipeline iteration. This stage closes the loop and prepares the system for a new cycle.
*   **Primary Inputs:** Authentication flags.
*   **Outputs:** Refreshed authenticated session state.
*   **Next Stage:** (Loop back to Stage 1) The pipeline is designed to restart, enabling continuous monitoring.
```