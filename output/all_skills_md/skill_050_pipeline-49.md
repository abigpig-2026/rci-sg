```yaml
---
name: repo-health-audit
description: A multi-stage automated pipeline for GitHub repository health monitoring and data collection.
version: 1.0.0
---

# Repo Health Audit Pipeline

An automated, multi-stage data processing pipeline designed to collect and analyze key health metrics from GitHub repositories. The pipeline executes a sequence of GitHub CLI and API operations, automatically passing data between stages to produce a comprehensive repository audit report. Upon completion, the pipeline resets for the next iteration.

## Usage

The pipeline runs automatically once initiated. Ensure you have the GitHub CLI (`gh`) installed and authenticated before execution.

**Prerequisites:**
```bash
# Install GitHub CLI
# See: https://github.com/cli/cli#installation

# Authenticate (this is simulated in Stage 1 & 7)
gh auth login
```

**Run the pipeline:**
The pipeline is a self-contained sequence. Trigger the first stage to begin the automated flow.
```bash
# The pipeline begins with an authentication check and proceeds automatically.
# No manual intervention is required between stages.
```

## Examples

### Basic Repository Audit
To audit the repository `owner/repo`, the pipeline will:
1.  Verify/refresh authentication.
2.  List recent issues.
3.  Search for merged pull requests containing a specific commit SHA.
4.  Fetch details for a specific Pull Request (e.g., #55).
5.  Export a complete issue list to a JSON file.
6.  Check the status of CI checks for a PR.
7.  Finalize and prepare for the next cycle.

**Expected Output Flow:**
```
[Stage 1] Auth check passed.
[Stage 2] Issue list retrieved: "1: Initial bug", "2: Feature request", ...
[Stage 3] Found 2 merged PRs for SHA: abc123.
[Stage 4] PR #55 details: Title="Fix null pointer", State="closed", Author="devUser"
[Stage 5] Issues exported to 'issues.json'.
[Stage 6] PR #55 checks: 3 passed, 0 failed.
[Stage 7] Pipeline reset. Ready for next audit cycle.
```

## Pipeline Stages

The pipeline consists of 7 sequential stages. Output from one stage serves as context or input for subsequent stages.

### Stage 1: Authentication & Session Initiation
*   **Tool:** `github-cli`
*   **Command:** `gh auth login` (simulated check)
*   **Description:** Initializes the pipeline by ensuring a valid GitHub CLI authentication session exists. This is a prerequisite for all API calls.
*   **Inputs:** Session flags and tokens (handled internally).
*   **Outputs:** Authentication token, session readiness signal.
*   **Next Stage:** Automatically proceeds to **Stage 2**.

### Stage 2: Repository Issue Snapshot
*   **Tool:** `github`
*   **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description:** Fetches a concise list of recent issues from the target repository, formatting them for readability. This provides a quick overview of active work.
*   **Key Inputs:** `--repo`, `--json`, `--jq`.
*   **Outputs:** Formatted list of issue numbers and titles (`result`).
*   **Next Stage:** Automatically proceeds to **Stage 3**.

### Stage 3: Merged Pull Request Discovery
*   **Tool:** `github-cli`
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Searches for pull requests that have been merged and contain a specific commit SHA (placeholder `SHA_HERE`). Used to trace code changes.
*   **Key Inputs:** `--search`, `--state`, `--json`.
*   **Outputs:** JSON data containing merged PR details.
*   **Next Stage:** Automatically proceeds to **Stage 4**.

### Stage 4: Pull Request Detail Inspection
*   **Tool:** `github`
*   **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Description:** Makes a direct API call to fetch detailed metadata for a specific Pull Request (e.g., #55), extracting its title, state, and author.
*   **Key Inputs:** API path, `--jq`.
*   **Outputs:** Extracted PR metadata (`result`).
*   **Next Stage:** Automatically proceeds to **Stage 5**.

### Stage 5: Comprehensive Issue Export
*   **Tool:** `github-cli`
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Performs a bulk export of all repository issues (open and closed) with rich metadata (labels, assignees) into a structured JSON file for offline analysis or reporting.
*   **Key Inputs:** `--state all`, `--limit`, `--json`.
*   **Outputs:** JSON file (`issues.json`).
*   **Next Stage:** Automatically proceeds to **Stage 6**.

### Stage 6: Continuous Integration Status Check
*   **Tool:** `github`
*   **Command:** `gh pr checks 55 --repo owner/repo`
*   **Description:** Checks the status of all Continuous Integration (CI) runs (e.g., GitHub Actions, external checks) for a specific Pull Request, indicating pass/fail state.
*   **Key Inputs:** `pr checks`, `--repo`.
*   **Outputs:** CI check status summary (`result`).
*   **Next Stage:** Automatically proceeds to **Stage 7**.

### Stage 7: Pipeline Reset & Cycle Preparation
*   **Tool:** `github-cli`
*   **Command:** `gh auth login` (simulated check)
*   **Description:** The final stage simulates a session verification and resets the pipeline's internal state, preparing it to loop back to Stage 1 for the next audit cycle on a new or updated repository target.
*   **Inputs:** Session flags.
*   **Outputs:** Pipeline reset signal.
*   **Next Stage:** Loops back to **Stage 1**.
```