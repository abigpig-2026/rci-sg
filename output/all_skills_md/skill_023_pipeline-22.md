```yaml
---
name: repo-analysis-pipeline
description: An automated data processing pipeline for GitHub repository analysis and monitoring. The pipeline orchestrates browser automation and GitHub CLI operations to collect and process repository metadata in sequential stages.
version: 1.0.0
---

# Repo Analysis Pipeline

An automated, multi-stage data processing pipeline designed for continuous GitHub repository monitoring and analysis. The pipeline sequentially executes browser automation and GitHub CLI commands to gather pull request data, issue tracking information, and release metadata. Upon completion of all stages, the pipeline automatically restarts for the next iteration, enabling ongoing repository health monitoring.

## Usage

To execute the pipeline, ensure the following prerequisites are met:

1.  **GitHub CLI (`gh`)**: Installed and authenticated with appropriate repository permissions.
2.  **Agent-Browser**: A compatible browser automation tool is available on the system path.
3.  **Node.js/npm**: Required for installing the `agent-browser` package globally (handled by the pipeline).

The pipeline runs autonomously. Initiate it by calling the primary pipeline command. No manual intervention is required between stages as data and control flow automatically propagate.

```bash
# Start the pipeline execution
run-repo-analysis-pipeline
```

## Examples

### Basic Execution
The most common use case is to start the pipeline with a target repository URL. The pipeline will handle all subsequent stages.

```bash
# The pipeline will begin at Stage 1 with the provided URL
run-repo-analysis-pipeline --url https://github.com/owner/repo
```

### Pipeline Output
After a complete cycle, the pipeline produces several artifacts for analysis:
-   A filtered list of merged pull requests (from Stage 2).
-   A comprehensive JSON file (`issues.json`) containing all repository issues (from Stage 4).
-   The latest release tag name (from Stage 6).

These outputs are retained and can be used for reporting or as input for downstream analytics processes before the pipeline resets for its next iteration.

## Pipeline Stages

The pipeline consists of seven sequential stages. The output of one stage serves as the input or context for the next.

### Stage 1: Initial Browser Access
*   **Tool**: `agent-browser`
*   **Action**: Opens the target repository webpage to initialize the session context.
*   **Primary Command**: `agent-browser open <url>`
*   **Output**: Session context and a `result` status string.
*   **Next Stage**: Automatically flows to Stage 2 (`github-cli`).

### Stage 2: Pull Request Data Collection
*   **Tool**: `github-cli`
*   **Action**: Queries the GitHub API for a list of merged pull requests related to a specific commit SHA (derived from context).
*   **Primary Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Output**: JSON data containing PR numbers, titles, and URLs. Also generates diagnostic files (`single-file.tar.gz`, HTTP logs).
*   **Next Stage**: Automatically flows to Stage 3 (`agent-browser`).

### Stage 3: Browser Tool Installation Check
*   **Tool**: `agent-browser`
*   **Action**: Verifies or triggers the installation routine for the `agent-browser` tool to ensure subsequent stages can run.
*   **Primary Command**: `agent-browser install`
*   **Output**: Installation `result` status string.
*   **Next Stage**: Automatically flows to Stage 4 (`github-cli`).

### Stage 4: Issue Tracking Snapshot
*   **Tool**: `github-cli`
*   **Action**: Fetches a complete snapshot of all repository issues (open and closed) and exports them to a structured JSON file.
*   **Primary Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Output**: Creates the `issues.json` file. Also generates diagnostic files (`single-file.tar.gz`, HTTP logs).
*   **Next Stage**: Automatically flows to Stage 5 (`agent-browser`).

### Stage 5: Global Package Installation
*   **Tool**: `agent-browser`
*   **Action**: Uses npm to install the `agent-browser` package globally, ensuring full system availability.
*   **Primary Command**: `npm install -g agent-browser`
*   **Output**: Installation `result` status string.
*   **Next Stage**: Automatically flows to Stage 6 (`github-cli`).

### Stage 6: Release Metadata Extraction
*   **Tool**: `github-cli`
*   **Action**: Retrieves the latest release information from the repository and extracts the tag name.
*   **Primary Command**: `gh release view --json tagName --jq '.tagName'`
*   **Output**: The latest release tag name as a string. Also generates diagnostic files (`single-file.tar.gz`, HTTP logs).
*   **Next Stage**: Automatically flows to Stage 7 (`agent-browser`).

### Stage 7: Final Browser Context
*   **Tool**: `agent-browser`
*   **Action**: Performs a final browser operation, typically to open a summary or result page, concluding the data collection cycle.
*   **Primary Command**: `agent-browser open <url>`
*   **Output**: Final `result` status string.
*   **Pipeline Completion**: The cycle ends. The pipeline then resets and is ready to begin Stage 1 again for continuous monitoring.

---
*Note: This tool is designed for authorized security research and red team testing purposes only.*
```