```yaml
---
name: issue-tracker-pipeline
description: A multi-stage automated data processing pipeline for monitoring GitHub issues and performing related web operations. The pipeline cycles through browser automation and GitHub API interactions to collect and process repository data.
version: 1.0.0
---

# Issue Tracker Pipeline

## Overview

The Issue Tracker Pipeline is an automated, multi-stage data processing workflow. It orchestrates a sequence of operations between a web browser agent and the GitHub CLI (`gh`) to monitor repository activity. Each stage processes data and passes its output as input to the next stage. Upon completion of the final stage, the pipeline automatically restarts for continuous, iterative monitoring.

## Usage

To execute the pipeline, invoke the primary pipeline command. The pipeline manages its own state and data flow between stages.

```bash
# Start the pipeline
issue-tracker-pipeline run

# Run the pipeline for a specific number of iterations
issue-tracker-pipeline run --iterations 5

# View pipeline status
issue-tracker-pipeline status
```

## Examples

### Basic Execution
This example runs the pipeline once through its complete five-stage cycle.

```bash
$ issue-tracker-pipeline run
[INFO] Starting Issue Tracker Pipeline...
[STAGE 1] Opening target webpage: https://example.com
[STAGE 2] Fetching issue list from owner/repo...
[STAGE 3] Installing browser dependencies...
[STAGE 4] Fetching details for Pull Request #55...
[STAGE 5] Re-opening target webpage for verification...
[INFO] Pipeline cycle complete. Restarting...
```

### Integration with External Tools
The pipeline's string output (`result`) from each stage can be piped to other command-line tools for further analysis.

```bash
# Run pipeline and filter for specific issue keywords
issue-tracker-pipeline run | grep -i "bug"
```

## Pipeline Stages

The pipeline consists of five sequential stages. The output (`result`) of each stage is passed as contextual input to the subsequent stage.

### Stage 1: Web Initialization
*   **Agent:** `agent-browser`
*   **Action:** Opens the initial target URL (`https://example.com`) to establish a browser session and load the web environment.
*   **Input:** Contextual parameters for browser control (e.g., `url`, `session`).
*   **Output:** A `result` string (e.g., page load status) passed to Stage 2.
*   **Next Stage:** GitHub (Stage 2)

### Stage 2: Issue List Fetch
*   **Agent:** `github` (GitHub CLI)
*   **Action:** Executes `gh issue list` on the specified repository (`owner/repo`) to retrieve a list of open issues. Output is formatted using `jq`.
*   **Input:** Takes the `result` from Stage 1 as context. Uses parameters like `repo`, `json`, and `jq`.
*   **Output:** A `result` string containing the formatted list of issues (e.g., `"123: Fix login bug\n124: Update docs"`), passed to Stage 3.
*   **Next Stage:** agent-browser (Stage 3)

### Stage 3: Environment Preparation
*   **Agent:** `agent-browser`
*   **Action:** Prepares the browser environment by installing necessary dependencies (`--with-deps`), ensuring readiness for complex web operations.
*   **Input:** Takes the `result` (issue list) from Stage 2 as context. Uses the `with-deps` flag.
*   **Output:** A `result` string (e.g., installation logs) passed to Stage 4.
*   **Next Stage:** GitHub (Stage 4)

### Stage 4: Pull Request Inspection
*   **Agent:** `github` (GitHub CLI)
*   **Action:** Uses the GitHub API (`gh api`) to fetch detailed information about a specific pull request (e.g., PR #55), extracting its title, state, and author.
*   **Input:** Takes the `result` from Stage 3 as context. Uses parameters like `jq` for output formatting.
*   **Output:** A `result` string with PR details (e.g., `"Update UI components\nopen\nalicej"`), passed to Stage 5.
*   **Next Stage:** agent-browser (Stage 5)

### Stage 5: Verification & Continuation
*   **Agent:** `agent-browser`
*   **Action:** Re-opens the target URL (`https://example.com`). This serves as a verification step and resets the browser context for the next pipeline cycle.
*   **Input:** Takes the `result` (PR details) from Stage 4 as context.
*   **Output:** A `result` string (final page status). This output concludes the cycle.
*   **Next Stage:** The pipeline loops back to **Stage 1** to begin the next iteration, creating a continuous monitoring loop.
```