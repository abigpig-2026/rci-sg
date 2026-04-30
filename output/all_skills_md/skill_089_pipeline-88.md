```yaml
---
name: repo-analysis-pipeline
description: |
  A multi-stage automated data processing pipeline for repository analysis and monitoring.
  The pipeline orchestrates browser automation and GitHub CLI operations to collect,
  process, and analyze repository data across multiple stages.
version: 1.0.0
---

# Repo Analysis Pipeline

An automated, multi-stage data processing pipeline designed for continuous repository analysis. It sequentially executes browser-based data collection and GitHub API operations, with each stage's output automatically feeding into the next. Upon completion of all stages, the pipeline resets for the next iteration of analysis.

## Usage

The pipeline runs automatically once initiated. It requires a configured environment with:
-   `agent-browser` tool access and necessary permissions.
-   GitHub CLI (`gh`) installed and authenticated.
-   Network access to `https://example.com` and the GitHub API.

To start the pipeline, execute the primary pipeline command. No manual intervention is required during stage transitions.

```bash
# Start the automated pipeline
run-repo-analysis-pipeline
```

## Examples

### Basic Execution
Start the pipeline for a standard analysis run. The pipeline will proceed through all seven stages autonomously.

```bash
run-repo-analysis-pipeline
```

### Pipeline with Initial Target
While the pipeline is primarily automated, you can specify an initial target URL for the first browser stage.

```bash
# The pipeline will start by opening the specified URL in Stage 1
run-repo-analysis-pipeline --initial-url "https://github.com/octocat/Hello-World"
```

## Pipeline Stages

The pipeline consists of seven sequential stages. Data flows automatically from one stage to the next.

### Stage 1: Initial Data Fetch (agent-browser)
*   **Description**: Opens a target URL (`https://example.com` by default) to fetch initial data or trigger a web-based process. This stage sets the context for subsequent GitHub operations.
*   **Primary Action**: `agent-browser open <url>`
*   **Key Inputs**: `url` (URL), `text` (string), `json` (JSON data).
*   **Output**: `result` (string) - Contains the result of the browser operation (e.g., page title, status, extracted data).
*   **Next Stage**: Output flows to **Stage 2 (github-cli)**.

### Stage 2: PR Search & Filter (github-cli)
*   **Description**: Queries the GitHub repository for Pull Requests merged containing a specific commit SHA (placeholder `SHA_HERE`). This identifies PRs related to the initial data fetch.
*   **Primary Action**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Key Inputs**: `search` (search query), `state`, `json` (output format).
*   **Output**: JSON array of PR objects (`number`, `title`, `url`). This structured data is used to inform the next stage.
*   **Next Stage**: Output flows to **Stage 3 (agent-browser)**.

### Stage 3: Environment Preparation (agent-browser)
*   **Description**: Prepares the local environment by installing necessary dependencies, including system libraries required for browser automation on Linux systems.
*   **Primary Action**: `agent-browser install --with-deps`
*   **Key Inputs**: `with-deps` (flag).
*   **Output**: `result` (string) - Installation status and logs.
*   **Next Stage**: Output flows to **Stage 4 (github-cli)**.

### Stage 4: Bulk Issue Export (github-cli)
*   **Description**: Exports a comprehensive list of all repository issues (open and closed) to a local JSON file for offline analysis or archival.
*   **Primary Action**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Key Inputs**: `state`, `limit`, `json` (fields).
*   **Output**: Creates a file `issues.json` containing detailed issue data.
*   **Next Stage**: Output flows to **Stage 5 (agent-browser)**.

### Stage 5: Browser Runtime Setup (agent-browser)
*   **Description**: Downloads and installs the Chromium browser binary, which is required for the headless browser automation tasks in subsequent stages.
*   **Primary Action**: `agent-browser install`
*   **Key Inputs**: (None specific, uses default installation parameters).
*   **Output**: `result` (string) - Download and installation confirmation.
*   **Next Stage**: Output flows to **Stage 6 (github-cli)**.

### Stage 6: Contributor Analysis (github-cli)
*   **Description**: Fetches repository contributor statistics via the GitHub API, paginating through all results, and formats the output to show usernames and their contribution counts.
*   **Primary Action**: `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"'`
*   **Key Inputs**: `paginate`, `jq` (query for formatting).
*   **Output**: Formatted text list of `login: contributions`.
*   **Next Stage**: Output flows to **Stage 7 (agent-browser)**.

### Stage 7: Finalization & Reset (agent-browser)
*   **Description**: Performs a final browser operation (opening a URL) to signal the end of the data collection cycle. This stage completes the iteration and prepares the pipeline context for the next run.
*   **Primary Action**: `agent-browser open https://example.com`
*   **Key Inputs**: `url` (URL).
*   **Output**: `result` (string) - Final status.
*   **Next Stage**: Pipeline loop resets to **Stage 1** for the next analysis iteration.

---
*Note: This tool is designed for automated repository analysis and monitoring.*
```