---
name: repo-ci-pipeline
description: A multi-stage automated data processing pipeline for repository CI/CD monitoring and issue tracking.
version: 1.0.0
---

# Repo CI Pipeline

An automated, multi-stage data processing pipeline designed to monitor GitHub repository activity, track issues and pull requests, and manage CI/CD workflows. The pipeline orchestrates browser automation and GitHub CLI operations in a sequential flow, automatically passing data between stages. Upon completion of all stages, the pipeline resets for the next iteration of monitoring and optimization.

## Usage

To execute the pipeline, you must have the required tools installed and configured:
- `agent-browser` (globally installed via npm)
- GitHub CLI (`gh`) authenticated with appropriate repository permissions

The pipeline runs sequentially. Provide the initial target repository URL as the starting input.

**Basic Command:**
```bash
# The pipeline is triggered by its first stage, typically requiring a target URL.
# Example: Starting the pipeline flow
pipeline-trigger --url "https://github.com/owner/repo"
```

**Environment Variables:**
- `GITHUB_TOKEN`: A valid GitHub Personal Access Token for `gh` CLI operations.
- `REPO_URL`: The target repository URL (can be passed as an argument).

## Examples

### Example 1: Full Pipeline Execution for a Repository
This example demonstrates a complete run targeting a specific repository.

```bash
# Set the target repository (this initiates Stage 1)
export REPO_URL="https://github.com/example/project"

# The pipeline will automatically execute the following sequence:
# 1. agent-browser opens the repository URL.
# 2. gh CLI searches for merged PRs containing a specific commit SHA.
# 3. agent-browser performs an installation/update check.
# 4. gh CLI exports all repository issues to a JSON file.
# 5. agent-browser ensures the global npm package is installed.
# 6. gh CLI monitors a CI run and sends a desktop notification upon completion.
# 7. agent-browser opens a final status page.
```

### Example 2: Integrating with a CI Scheduler
Run the pipeline on a schedule (e.g., via cron) to collect daily metrics.

```bash
# Cron job running every 6 hours
0 */6 * * * /path/to/pipeline-trigger --url "https://github.com/org/main-repo" --output-dir /var/log/pipeline-runs
```

## Pipeline Stages

The pipeline consists of seven sequential stages. Data flows from the output of one stage to the input of the next.

### Stage 1: Repository Initialization
*   **Tool:** `agent-browser`
*   **Command:** `agent-browser open <url>`
*   **Description:** Opens the target repository URL in a browser context to initialize the session and retrieve page content.
*   **Input:** Target repository URL.
*   **Output:** A `result` string containing page status or content.
*   **Next Stage:** Stage 2 (github-cli).

### Stage 2: Pull Request Analysis
*   **Tool:** `github-cli`
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Queries the GitHub API for pull requests that have been merged and contain a specific commit SHA. Outputs structured JSON data.
*   **Input:** Context from Stage 1 (implicitly uses the authenticated repo).
*   **Output:** JSON data containing PR numbers, titles, and URLs. May also output debug files or raw HTTP logs.
*   **Next Stage:** Stage 3 (agent-browser).

### Stage 3: Environment Verification
*   **Tool:** `agent-browser`
*   **Command:** `agent-browser install`
*   **Description:** Verifies or performs a local installation step for the `agent-browser` tool, ensuring the environment is prepared for subsequent browser operations.
*   **Input:** Status/context from previous stages.
*   **Output:** A `result` string indicating installation status.
*   **Next Stage:** Stage 4 (github-cli).

### Stage 4: Issue Data Export
*   **Tool:** `github-cli`
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Fetches a comprehensive list of all repository issues (open and closed) and exports them to a `issues.json` file for offline analysis or reporting.
*   **Input:** Context from the active repository session.
*   **Output:** A file (`issues.json`) containing issue data and potential auxiliary debug outputs.
*   **Next Stage:** Stage 5 (agent-browser).

### Stage 5: Tooling Update
*   **Tool:** `agent-browser`
*   **Command:** `npm install -g agent-browser`
*   **Description:** Ensures the latest version of the `agent-browser` npm package is installed globally, maintaining tool currency.
*   **Input:** Context from the pipeline.
*   **Output:** A `result` string with npm installation logs.
*   **Next Stage:** Stage 6 (github-cli).

### Stage 6: CI Workflow Monitoring
*   **Tool:** `github-cli`
*   **Command:** `gh run watch && notify-send "CI done!"`
*   **Description:** Monitors the latest GitHub Actions workflow run in real-time and sends a system notification upon completion. This stage focuses on CI/CD pipeline observation.
*   **Input:** Context from the repository.
*   **Output:** CI run status, potential archive files, and JSON response data.
*   **Next Stage:** Stage 7 (agent-browser).

### Stage 7: Final Status Review
*   **Tool:** `agent-browser`
*   **Command:** `agent-browser open <url>`
*   **Description:** Opens a final webpage (e.g., repository homepage, CI results page) to provide a visual status review, closing the automation loop.
*   **Input:** A URL, typically derived from previous stages' outputs.
*   **Output:** A `result` string confirming the page was opened.
*   **Next Stage:** Pipeline completes and resets for the next iteration.

---
*Note: This tool is designed for automated repository monitoring and data aggregation. Ensure you have proper authorization to access and interact with the target repositories.*