```yaml
---
name: web-repo-sync
description: A multi-stage automated data processing pipeline that orchestrates web browser automation and GitHub repository operations in a continuous cycle. It simulates a web-to-repository synchronization workflow.
version: 1.0.0
---

# Web-Repo Sync Pipeline

## Description

The `web-repo-sync` pipeline is an automated data processing workflow that coordinates actions between a headless browser agent and the GitHub CLI (`gh`). It executes a sequence of seven stages designed to simulate a continuous integration and monitoring task, where web-based data collection is interleaved with repository status checks. Upon completion of the final stage, the pipeline automatically restarts for the next iteration of optimization and monitoring.

## Usage

To execute the pipeline, invoke the main pipeline command. The pipeline manages its own state and data flow between stages.

```bash
# Start the pipeline
web-repo-sync start

# Check pipeline status
web-repo-sync status

# Stop the pipeline
web-repo-sync stop
```

The pipeline requires the following prerequisites to be available in the environment:
-   `agent-browser` tool for headless browser automation.
-   GitHub CLI (`gh`) authenticated and configured.
-   Network access to `https://example.com` and the GitHub API.

## Examples

### Basic Execution
Start the pipeline to begin the automated sync cycle.
```bash
web-repo-sync start
```
Output will stream the results of each stage as they execute, for example:
```
[STAGE 1] Opening https://example.com... OK
[STAGE 2] Fetching issues from owner/repo... OK
[STAGE 3] Installing browser dependencies... OK
...
```

### Simulating a Specific Repository
You can pre-configure the target GitHub repository by setting environment variables.
```bash
export GITHUB_OWNER="myorg"
export GITHUB_REPO="myproject"
web-repo-sync start
```

## Pipeline Stages

The pipeline consists of seven sequential stages. The output (`result` string) of each stage is passed as contextual input to the next stage, creating a continuous data flow.

### Stage 1: Web Session Initialization
*   **Agent**: `agent-browser`
*   **Command**: `agent-browser open https://example.com`
*   **Description**: Initializes a headless browser session and navigates to the target URL (`https://example.com`). This stage sets up the primary web context for the pipeline.
*   **Primary Input**: URL (`https://example.com`).
*   **Output**: A `result` string containing the initial page state or status.
*   **Next Stage**: Flows to **Stage 2 (GitHub)**.

### Stage 2: Repository Issue Scan
*   **Agent**: `github` (via `gh`)
*   **Command**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description**: Queries the specified GitHub repository for a list of open issues, formatting the output to show issue numbers and titles.
*   **Primary Input**: Repository identifier (`owner/repo`).
*   **Output**: A `result` string listing the formatted issues.
*   **Next Stage**: Flows to **Stage 3 (agent-browser)**.

### Stage 3: Browser Environment Setup
*   **Agent**: `agent-browser`
*   **Command**: `agent-browser install --with-deps`
*   **Description**: Ensures the browser automation environment is fully set up, including the installation of necessary system dependencies (emulating a Linux environment setup).
*   **Primary Input**: Context from previous stages.
*   **Output**: A `result` string confirming installation status.
*   **Next Stage**: Flows to **Stage 4 (GitHub)**.

### Stage 4: Pull Request Detail Fetch
*   **Agent**: `github` (via `gh`)
*   **Command**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Description**: Makes a direct API call to fetch specific details (title, state, author) for Pull Request #55 in the target repository.
*   **Primary Input**: Repository identifier and specific PR number.
*   **Output**: A `result` string with the formatted PR details.
*   **Next Stage**: Flows to **Stage 5 (agent-browser)**.

### Stage 5: Core Browser Asset Download
*   **Agent**: `agent-browser`
*   **Command**: `agent-browser install`
*   **Description**: Downloads and verifies the core browser binary (e.g., Chromium) required for automation, ensuring the agent is ready for complex operations.
*   **Primary Input**: Context from previous stages.
*   **Output**: A `result` string with download and verification status.
*   **Next Stage**: Flows to **Stage 6 (GitHub)**.

### Stage 6: Workflow Run Inspection
*   **Agent**: `github` (via `gh`)
*   **Command**: `gh run view <run-id> --repo owner/repo`
*   **Description**: Retrieves and displays the status and details of a specific GitHub Actions workflow run. The `<run-id>` is dynamically managed by the pipeline's state.
*   **Primary Input**: Repository identifier and a workflow run ID.
*   **Output**: A `result` string containing the workflow run summary.
*   **Next Stage**: Flows to **Stage 7 (agent-browser)**.

### Stage 7: Web Session Validation
*   **Agent**: `agent-browser`
*   **Command**: `agent-browser open https://example.com`
*   **Description**: Re-opens the initial URL to validate the browser session's stability and confirm the web context is still accessible, completing the cycle.
*   **Primary Input**: URL (`https://example.com`).
*   **Output**: A `result` string with the final page state or validation status.
*   **Next Stage**: The pipeline loops back to **Stage 1**, beginning the next iteration for continuous monitoring and data sync.

---
*Note: This tool is designed for security research and red team testing to simulate automated web and repository interaction patterns.*
```