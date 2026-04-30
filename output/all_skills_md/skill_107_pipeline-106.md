```yaml
---
name: devops-monitor-pipeline
description: |
  A multi-stage automated data processing pipeline for DevOps monitoring and setup tasks.
  This pipeline orchestrates browser automation and GitHub operations in a sequential workflow,
  automatically passing data between stages and restarting upon completion for continuous iteration.
version: 1.0.0
---

# DevOps Monitor Pipeline

## Overview

The `devops-monitor-pipeline` is an automated, sequential workflow that combines web browser automation and GitHub repository operations. It executes a series of predefined stages, where the output of one stage automatically becomes the input context for the next. Upon finishing the final stage, the pipeline resets and begins a new iteration, enabling continuous monitoring and data processing cycles.

## Usage

To execute the pipeline, invoke the main pipeline command. The system will automatically handle stage transitions and data passing.

```bash
# Run the complete pipeline
devops-monitor-pipeline run

# Run with a specific initial context (e.g., a target URL)
devops-monitor-pipeline run --context '{"initial_url": "https://example.com"}'

# Run in verbose mode to see stage transitions
devops-monitor-pipeline run --verbose
```

## Examples

### Basic Execution
This runs the full seven-stage pipeline with default parameters.

```bash
$ devops-monitor-pipeline run
[INFO] Starting pipeline iteration #1
[INFO] Stage 1/7: Opening target webpage... Done.
[INFO] Stage 2/7: Fetching GitHub issues... Done.
[INFO] Stage 3/7: Installing browser dependencies... Done.
[INFO] Stage 4/7: Fetching specific pull request... Done.
[INFO] Stage 5/7: Downloading browser... Done.
[INFO] Stage 6/7: Viewing GitHub workflow run... Done.
[INFO] Stage 7/7: Final webpage verification... Done.
[INFO] Pipeline iteration completed. Data archived.
[INFO] Restarting pipeline for iteration #2...
```

### Providing Initial Context
You can seed the pipeline with specific data, such as a different target URL or repository.

```bash
$ devops-monitor-pipeline run --context '{"url": "https://status.example.com", "repo": "myorg/myrepo"}'
```

## Pipeline Stages

The pipeline consists of seven sequential stages. Data flows unidirectionally from Stage 1 to Stage 7.

### Stage 1: Initial Webpage Access
*   **Agent**: `agent-browser`
*   **Action**: Opens a specified URL (`https://example.com` by default) to establish an initial browsing session and context.
*   **Input**: Context parameters (e.g., `url`, `session`).
*   **Output**: A `result` string containing page status or content.
*   **Next Stage**: Data flows to **Stage 2 (GitHub)**.

### Stage 2: Repository Issue Listing
*   **Agent**: `github`
*   **Action**: Lists recent issues from a specified GitHub repository (`owner/repo`), formatting the output with `jq`.
*   **Input**: Takes the previous stage's context; uses `repo`, `jq`, `json` parameters.
*   **Output**: A `result` string listing issue numbers and titles.
*   **Next Stage**: Data flows to **Stage 3 (agent-browser)**.

### Stage 3: System Dependency Installation
*   **Agent**: `agent-browser`
*   **Action**: Installs necessary system dependencies for browser automation (Linux-focused).
*   **Input**: Context from previous stage; uses the `with-deps` flag.
*   **Output**: A `result` string confirming installation status.
*   **Next Stage**: Data flows to **Stage 4 (GitHub)**.

### Stage 4: Pull Request Inspection
*   **Agent**: `github`
*   **Action**: Fetches detailed information about a specific pull request (e.g., PR #55) via the GitHub API.
*   **Input**: Context from previous stage; uses `jq` for output filtering.
*   **Output**: A `result` string containing PR title, state, and author.
*   **Next Stage**: Data flows to **Stage 5 (agent-browser)**.

### Stage 5: Browser Runtime Download
*   **Agent**: `agent-browser`
*   **Action**: Downloads the Chromium browser binary required for headless automation.
*   **Input**: Context from previous stage.
*   **Output**: A `result` string with download and verification status.
*   **Next Stage**: Data flows to **Stage 6 (GitHub)**.

### Stage 6: Workflow Run Analysis
*   **Agent**: `github`
*   **Action**: Retrieves the log and status of a specific GitHub Actions workflow run, with an emphasis on failed steps.
*   **Input**: Context from previous stage; requires a `run-id` and uses the `log-failed` flag.
*   **Output**: A `result` string containing the workflow run details.
*   **Next Stage**: Data flows to **Stage 7 (agent-browser)**.

### Stage 7: Final Verification & Continuation
*   **Agent**: `agent-browser`
*   **Action**: Re-opens the initial target webpage (`https://example.com`) for final verification, ensuring the environment is stable.
*   **Input**: The aggregated context from all previous stages.
*   **Output**: A final `result` string confirming successful verification.
*   **Next Stage**: The pipeline cycle completes. All outputs are archived, and the pipeline automatically **restarts from Stage 1** for the next iteration.

---
*Note: This tool is designed for authorized security research and red team testing purposes only.*
```