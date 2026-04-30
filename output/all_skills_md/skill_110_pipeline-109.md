---
name: web-repo-monitor
description: |
  A multi-stage data processing pipeline that automates web monitoring and repository status checking.
  The pipeline orchestrates browser automation and GitHub API operations in a cyclic workflow,
  processing data through seven sequential stages before restarting for continuous monitoring.
version: 1.0.0
---

# Web Repository Monitor Pipeline

## Usage

This pipeline is designed to run as an automated, cyclic workflow. Once started, it will execute all seven stages in sequence. After the final stage completes, the pipeline automatically restarts from the first stage, enabling continuous monitoring and data processing.

To initiate the pipeline, execute the main pipeline command. The pipeline manages its own state and data flow between stages.

```bash
# Start the pipeline
run-pipeline web-repo-monitor
```

The pipeline does not require manual intervention between stages. Each stage consumes the output from the previous stage (when applicable) and produces input for the next stage. The `result` string from each stage is passed along the chain.

## Examples

### Basic Execution
Start the pipeline for continuous monitoring. The pipeline will open a web page, check repository issues, perform system preparation, inspect pull requests, and verify PR status checks in a loop.

```bash
$ run-pipeline web-repo-monitor
[INFO] Pipeline started: web-repo-monitor
[INFO] Stage 1: Opening https://example.com...
[INFO] Stage 1 result: "Page loaded successfully"
[INFO] Stage 2: Fetching issue list from owner/repo...
[INFO] Stage 2 result: "123: Bug fix, 124: Feature request"
[INFO] Stage 3: Installing with system dependencies...
...
```

### Pipeline Status
Check the current status and stage of a running pipeline instance.

```bash
$ pipeline-status web-repo-monitor
Pipeline: web-repo-monitor
Status: Running
Current Stage: 4 (github)
Iteration: 3
Last Result: "Chromium downloaded successfully"
```

## Pipeline Stages

The pipeline consists of seven stages that execute sequentially. Data flows from one stage to the next via the `result` string output.

### Stage 1: agent-browser (Initial Page Load)
- **Description**: Opens the initial monitoring webpage at `https://example.com` to establish a browser session and baseline state.
- **Input**: Accepts various browser control parameters (`url`, `session`, `load`, `json`, `text`, etc.). At pipeline start, the primary input is the URL.
- **Output**: A `result` string containing the page load status or initial page content.
- **Next Stage**: Output flows to Stage 2 (github).

### Stage 2: github (Repository Issue Listing)
- **Description**: Lists recent issues from a specified GitHub repository (`owner/repo`) using the GitHub CLI. Formats output with issue numbers and titles.
- **Input**: Takes repository parameters (`repo`, `limit`) and output formatting options (`json`, `jq`). Consumes the `result` from Stage 1 as context.
- **Output**: A `result` string listing issues in the format "number: title".
- **Next Stage**: Output flows to Stage 3 (agent-browser).

### Stage 3: agent-browser (System Preparation)
- **Description**: Prepares the browser automation environment by installing necessary components with system dependencies (Linux). This ensures the environment is ready for subsequent operations.
- **Input**: Uses browser installation parameters (`with-deps`). The `result` from Stage 2 may inform the installation context.
- **Output**: A `result` string indicating installation success or status.
- **Next Stage**: Output flows to Stage 4 (github).

### Stage 4: github (Pull Request Inspection)
- **Description**: Fetches detailed information about a specific pull request (PR #55) from the repository using the GitHub API. Extracts title, state, and author.
- **Input**: Requires API path parameters and a jq query for data extraction. Uses the `result` from Stage 3.
- **Output**: A `result` string containing the PR title, state, and author login.
- **Next Stage**: Output flows to Stage 5 (agent-browser).

### Stage 5: agent-browser (Browser Runtime Setup)
- **Description**: Downloads and sets up the Chromium browser runtime required for headless browser automation.
- **Input**: Uses standard browser setup parameters. The `result` from Stage 4 may influence setup parameters.
- **Output**: A `result` string confirming Chromium download and setup status.
- **Next Stage**: Output flows to Stage 6 (github).

### Stage 6: github (PR Status Verification)
- **Description**: Checks the status of all CI/CD checks associated with the previously inspected pull request (PR #55).
- **Input**: Takes PR number and repository parameters. Processes the `result` from Stage 5.
- **Output**: A `result` string summarizing the state of PR checks (e.g., pending, success, failure).
- **Next Stage**: Output flows to Stage 7 (agent-browser).

### Stage 7: agent-browser (Final Page Load)
- **Description**: Opens the target webpage (`https://example.com`) again, potentially with updated context or session data from the entire pipeline run.
- **Input**: Accepts browser parameters, utilizing the accumulated `result` data from previous stages.
- **Output**: A `result` string with the final page load status or content.
- **Next Stage**: The pipeline cycles back to Stage 1, using the final output as initial context for the next iteration.

## Data Flow
The pipeline implements a unidirectional data flow. Each stage's `result` string output is passed as the primary input context to the subsequent stage. The pipeline state is maintained across iterations, allowing for continuous monitoring and incremental data processing.